import logging
from typing import Union

from lxml import etree

logger = logging.getLogger('masterdata.mooncell.extractor')


class InfoExtractor:
    _wikitable_nomobile_logo = 'wikitable nomobile logo'
    _wikitable_logo = 'wikitable logo'
    _wikitable_nomobile = 'wikitable nomobile'
    _wikitable = 'wikitable'
    _nomobile = 'nomobile'
    _mw_wikitable_nomobile = 'wikitable mw-collapsible mw-collapsed nomobile'

    def __init__(self, html: Union[bytes, str]):
        self.root = etree.HTML(html)

    def title(self):
        return self.root.xpath('/html/head/title/text()')[0]

    def extract(self, key: str = 'extract_') -> dict:
        info = {}
        drop_index = len(key)
        for fn_name in type(self).__dict__.keys():
            if fn_name.startswith(key):
                name = fn_name[drop_index:]
                extract_fn = getattr(self, fn_name)
                try:
                    res = extract_fn()
                except:
                    logger.error(
                        f'Failed to extract {name} in "{self.title()}".')
                else:
                    info[name] = res
        return info


class MooncellIE(InfoExtractor):
    def elements_between(self, start: str, end: str = None):
        """Return a iterator of sibling elements between start and end section.
        End up with same tag of start section if end is None.
        """
        node = self.root.xpath(
            f'.//span[@class="mw-headline" and text()="{start}"]/..')
        if not node:
            return None
        node = node[0]
        stop_tag = node.tag
        while 1:
            node = node.getnext()
            if end:
                if node.xpath('string(.)') == end:
                    break
            else:
                tag = node.tag
                if tag == stop_tag or (not isinstance(tag, str)) or (
                        len(tag) > 1 and tag.startswith('h') and tag < stop_tag):
                    break
            yield node

    def tables_between(self, table_class: str, start: str, end: str = None, keep_struct=False):
        """Return a iterator of sibling tables between start and end section.
        End up with same tag of start section if end is None.
        """
        for node in self.elements_between(start, end):
            cls = node.get('class')
            if not cls and table_class is not None:
                continue
            if node.tag == 'div' and cls.startswith('tabber'):
                res = node.xpath(
                    f'descendant::table[starts-with(@class,"{table_class}")]')
                if keep_struct:
                    yield [table for table in res]
                else:
                    for table in res:
                        yield table
            elif node.tag == 'table' and table_class == cls:
                yield node
