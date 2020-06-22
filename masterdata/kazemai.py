import json
import logging
import re
from base64 import b64decode

from . import downloader

logger = logging.getLogger('masterdata.kazemai')
from .json2sqlite3 import JSDatabase


class Endpoints:
    raw_gh_pages = "https://raw.githubusercontent.com/KazeMai/fgo-vz/gh-pages/"

    @classmethod
    def master_js(cls) -> str:
        return f'{cls.raw_gh_pages}common/js/master.js'

    @classmethod
    def js_page(cls) -> str:
        return 'https://github.com/KazeMai/fgo-vz/tree/gh-pages/common/js'

    @classmethod
    def svtcomment(cls, svt_id) -> str:
        return f'{cls.raw_gh_pages}common/svtcomment/jp/{svt_id}'


def _decode_master_js(s: str) -> dict:
    from lzstring import LZString
    matched = re.search(
        r"convert_formated_hex_to_string\('(.*)'\)\);", s).group(1)
    # convert formatted hex to string
    compressed = ''.join(
        chr(int(matched[i:i + 2], 16) | (int(matched[i + 2:i + 4], 16) << 8))
        for i in range(0, len(matched) - 1, 4))
    del matched
    res = LZString().decompress(compressed)
    return json.loads(res)


def _decode_svtcomment(b: bytes) -> dict:
    decoded = str(b64decode(b), 'utf-8')
    comment = json.loads(decoded)
    return comment


def fetch_masterdata() -> dict:
    text = downloader.download_file(Endpoints.master_js()).decode('utf8')
    return _decode_master_js(text)


def master_js_id() -> str:
    f = downloader.download_file(Endpoints.js_page())
    text = f.decode('utf8')
    js_id = re.search(
        '(?<=title="master.js" id=").*?(?=")', text).group(0)
    return js_id


def fetch_comments(svt_ids):
    urls = [Endpoints.svtcomment(svt_id) for svt_id in svt_ids]
    files = downloader.download_files(urls)
    comments = [comment for file in files for comment in _decode_svtcomment(file)]
    return comments


def make_database(path: str = ':memory:') -> JSDatabase:
    db = JSDatabase(path)
    master_json = fetch_masterdata()
    db.load_json(master_json)
    query = "SELECT id FROM mstSvt WHERE (type=1 or type=2) and collectionNo>0;"
    svt_ids = [i[0] for i in db.con.execute(query)]
    comment_json = {'mstSvtComment': fetch_comments(svt_ids)}
    db.load_json(comment_json)
    return db
