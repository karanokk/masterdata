# -*- coding: utf-8 -*-
import re

from .base import MooncellExtractor


class RelatedQuestExtractor(MooncellExtractor):
    def extract_related_quests(self):
        def get_title(section_name):
            tables = self.find_tables(section_name, self.WT_LOGO)
            if not tables:
                return []
            return [table.xpath('string(tbody/tr[1]/th[2]/big)') for table in tables]

        return get_title('幕间物语') + get_title('强化任务')
