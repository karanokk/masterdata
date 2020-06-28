# -*- coding: utf-8 -*-
import unittest

from masterdata.mooncell.extractor import ServantIE, QuestIE


class TestExtractor(unittest.TestCase):

    def assertLen(self, lhs, count):
        self.assertEqual(len(lhs), count)

    def servant_ie(self, link_name) -> ServantIE:
        with open(f'./test/testdata/{link_name}.htm') as f:
            html = f.read()
        return ServantIE(html)

    def quest_ie(self, chapter) -> QuestIE:
        with open(f'./test/testdata/{chapter}.htm') as f:
            html = f.read()
        return QuestIE(html)

    def test_servant_extractor(self):
        # standard servant
        卫宫 = self.servant_ie('卫宫').extract()
        self.assertLen(卫宫['treasure_devices'], 2)
        self.assertLen(卫宫['skills'], 5)
        self.assertLen(卫宫['class_skills'], 2)
        self.assertLen(卫宫['ascension_materials'], 4)
        self.assertLen(卫宫['skill_materials'], 9)
        self.assertLen(卫宫['bond_stories'], 7)

        # non servant
        盖提亚 = self.servant_ie('盖提亚').extract()
        self.assertLen(盖提亚['treasure_devices'], 2)
        self.assertLen(盖提亚['skills'], 3)
        self.assertLen(盖提亚['bond_stories'], 7)

        # fool's day
        _ = self.servant_ie('保罗·班扬').extract()

        # special servant
        _ = self.servant_ie('玛修·基列莱特').extract()

    def test_quest_extractor(self):
        亚种3 = self.quest_ie('亚种特异点Ⅲ 尸山血河舞台 下总国_关卡配置').extract()
        self.assertLen(亚种3['main_quests'], 16)
        self.assertLen(亚种3['free_quests'], 9)

    def test_elements_between(self):
        ie = self.servant_ie('卫宫')
        r1 = list(ie.elements_between('宝具'))
        self.assertEqual(len(r1), 5)
        r2 = list(ie.elements_between('宝具', '职阶技能'))
        self.assertEqual(len(r2), 14)

    def test_tables_between(self):
        ie = self.servant_ie('卫宫')
        r1 = list(ie.tables_between(
            'wikitable nomobile logo', '宝具'))
        self.assertEqual(len(r1), 2)
        r2 = list(ie.tables_between(
            'wikitable nomobile logo', '宝具', '职阶技能'))
        self.assertEqual(len(r2), 7)
