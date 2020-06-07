import json
import logging
import re
from base64 import b64decode
from urllib.parse import urljoin
from urllib.request import urlopen

import aiohttp

from ..utils import AppSession
from .utils import decode_master_js

logger = logging.getLogger('masterdata.kazemai')


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


def get_masterdata() -> str:
    f = urlopen(KazemaiURL.master_js)
    text = f.read().decode('utf8')
    return decode_master_js(text)


async def async_get_svtcomment(svtId: int, session: aiohttp.ClientSession = AppSession.session()):
    url = urljoin(KazemaiURL.svtcomment_jp, str(svtId))
    async with session.get(url) as resp:
        if resp.status == 404:
            logger.warning(
                f'Servant comment for [{svtId}] not found.')
            return []
        else:
            b = await resp.read()
            decoded = str(b64decode(b), 'utf-8')
            comment = json.loads(decoded)
            return comment
