import json
import logging
import re
from base64 import b64decode
from urllib.parse import urljoin
from urllib.request import urlopen

import aiohttp

from .utils import decode_master_js
from ..utils import AppSession

logger = logging.getLogger('masterdata.kazemai')


class KazemaiURL:
    common = 'https://raw.githubusercontent.com/KazeMai/fgo-vz/gh-pages/common/'
    js_dir = 'https://github.com/KazeMai/fgo-vz/tree/gh-pages/common/js'
    master_js = urljoin(common, 'js/master.js')
    svt_comment_jp = urljoin(common, 'svtcomment/jp/')


def lastest_master_js_id() -> str:
    f = urlopen(KazemaiURL.js_dir)
    text = f.read().decode('utf8')
    latest_version = re.search(
        '(?<=title="master.js" id=").*?(?=")', text).group(0)
    return latest_version


def masterdata() -> dict:
    f = urlopen(KazemaiURL.master_js)
    text = f.read().decode('utf8')
    return decode_master_js(text)


async def async_get_svt_comment(svt_id: int, session: aiohttp.ClientSession = None):
    if not session:
        session = AppSession.session()
    url = urljoin(KazemaiURL.svt_comment_jp, str(svt_id))
    async with session.get(url) as resp:
        if resp.status == 404:
            logger.warning(
                f'Servant comment for [{svt_id}] not found.')
            return []
        else:
            b = await resp.read()
            decoded = str(b64decode(b), 'utf-8')
            comment = json.loads(decoded)
            return comment
