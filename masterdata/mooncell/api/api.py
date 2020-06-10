import re

from .MediaWikiEndpoint import MediaWikiEndpoint, ParseProp
from .model import MCEssenceCraftItem, MCServantItem

endpoint = MediaWikiEndpoint('https://fgo.wiki/api.php')


def get_page(page_name: str):
    page = endpoint.parse(ParseProp.text, page=page_name)
    return page["parse"]["text"]


async def async_get_page(page_name: str):
    page = await endpoint.async_parse(ParseProp.text, page=page_name)
    return page["parse"]["text"]


def get_servants():
    text = _match_csv_str('英灵图鉴')
    _, *rows = text.split('\\n')
    return [MCServantItem(row.split(',')) for row in rows]


def get_essence_crafts():
    text = _match_csv_str('礼装图鉴')
    _, *rows = text.split('\\n')
    return [MCEssenceCraftItem(row.split(',')) for row in rows]


def _match_csv_str(page_name: str):
    text = get_page(page_name)
    matched = re.search(r'var raw_str = "(.*)";', text)
    if matched:
        return matched.group(1)
    else:
        raise Exception('csv text not found')
