import asyncio
import json
import logging
import os
import re
from base64 import b64decode
from functools import reduce
from typing import List, Sequence
from urllib.parse import urljoin
from urllib.request import urlopen

from lzstring import LZString

from .utils import AppSession

logger = logging.getLogger('masterdata')


class KazemaiURL:
    common = 'https://raw.githubusercontent.com/KazeMai/fgo-vz/gh-pages/common/'
    js_dir = 'https://github.com/KazeMai/fgo-vz/tree/gh-pages/common/js'
    master_js = urljoin(common, 'js/master.js')
    svtcomment_jp = urljoin(common, 'svtcomment/jp/')


def get_lastest_master_js_id() -> str:
    f = urlopen(KazemaiURL.js_dir)
    text = f.read().decode('utf8')
    latest_version = re.search(
        '(?<=title="master.js" id=").*?(?=")', text).group(0)
    return latest_version


def _decode_master_js(s: str) -> dict:
    matched = re.search(
        r"convert_formated_hex_to_string\('(.*)'\)\);", s).group(1)
    # convert formatted hex to string
    compressed = ''.join(
        chr(int(matched[i:i + 2], 16) | (int(matched[i + 2:i + 4], 16) << 8))
        for i in range(0, len(matched) - 1, 4)
    )
    del matched
    res = LZString().decompress(compressed)
    return json.loads(res)


def fetch_masterdata() -> dict:
    f = urlopen(KazemaiURL.master_js)
    text = f.read().decode('utf8')
    return _decode_master_js(text)


def fetch_svtcomment(svtIds: Sequence[int]) -> List[dict]:
    async def get_comment(svtId: int, session):
        url = urljoin(KazemaiURL.svtcomment_jp, str(svtId))
        async with session.get(url) as resp:
            if resp.status == 404:
                logger.warning(
                    f'Servant comment for [{svtId}] not found.')
                return []
            else:
                b = await resp.read()
                # decode base64 json
                decoded = str(b64decode(b), 'utf-8')
                comment = json.loads(decoded)
                return comment

    loop = asyncio.get_event_loop()

    async def main():
        session = AppSession.session()
        tasks = (loop.create_task(get_comment(svtId, session))
                 for svtId in svtIds)
        return await asyncio.gather(*tasks)

    res = loop.run_until_complete(main())
    comments = reduce(lambda x, y: x + y, res)
    return comments
