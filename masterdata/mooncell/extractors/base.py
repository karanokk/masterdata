# -*- coding: utf-8 -*-
from lxml import etree


class MediaWikiExtractor(object):
    def __init__(self, html):
        """`html`起始于`<div class="mw-parser-output">`
        """
        self.root = etree.HTML(html)

    def find(self, section_name):
        """列出两个`h`节点之间的同级节点

        节点起始于`section_name`，结束于下个`h`节点
        """
        node = self.root.find(f'.//span[@id="{section_name}"]/..')
        if node is None:
            return None
        stop_tag = node.tag
        while 1:
            node = node.getnext()
            tag = node.tag
            if tag == stop_tag or (not isinstance(tag, str)) or (
                    len(tag) > 1 and tag.startswith('h') and tag < stop_tag):
                break
            yield node


class MooncellExtractor(MediaWikiExtractor):
    WT_NOMOBILE_LOGO = 'wikitable nomobile logo'
    WT_LOGO = 'wikitable logo'
    WT_NOMOBILE = 'wikitable nomobile'
    WT = 'wikitable'
    NOMOBILE = 'nomobile'
    WT_MW_NOMOBILE = 'wikitable mw-collapsible mw-collapsed nomobile'

    def __init__(self, html):
        super(MooncellExtractor, self).__init__(html)
        self.resource_domain = "https://fgo.wiki/w"

    def find_tables(self, section_name, table_class, keep_struct=False):
        """过滤出小节中的表格

        :params section_name: 小节的名称
        :params table_class: 表格的`class`
        :params keep_struct: 是否保持表格之间的层级结构，默认不保持，平级输出

        :yield: 表格节点
        """
        for node in self.find(section_name):
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