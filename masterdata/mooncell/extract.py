import logging
import re

from .extractor import ServantIE
from .. import downloader

logger = logging.getLogger('masterdata.mooncell')


class EndPoints:
    domain = "https://fgo.wiki/w/"

    @classmethod
    def page_with_name(cls, name):
        return f'{cls.domain}{name}'

    @classmethod
    def mission_page(cls, mission):
        return f'{cls.domain}{mission}/关卡配置'


def extract_servants(name_links=None):
    if not name_links:
        name_links = get_servant_name_links()
    urls = [EndPoints.page_with_name(name) for name in name_links]
    files = downloader.download_files(urls)
    return [ServantIE(file).extract() for file in files]


def get_servant_name_links():
    text = _match_csv_str(EndPoints.page_with_name('英灵图鉴'))
    _, *rows = text.split('\\n')
    return [row.split(',', maxsplit=6).pop(-2) for row in rows]


def get_essence_craft_name_links():
    text = _match_csv_str(EndPoints.page_with_name('礼装图鉴'))
    _, *rows = text.split('\\n')
    return [row.split(',', maxsplit=6).pop(-2) for row in rows]


def _match_csv_str(page_name: str):
    text = downloader.download_file(page_name).decode('utf8')
    matched = re.search(r'var raw_str = "(.*)";', text)
    if matched:
        return matched.group(1)
    else:
        raise Exception('csv text not found')
