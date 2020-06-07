# coding: utf-8

import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from masterdata import mooncell


class TestMooncell(unittest.TestCase):
    def test_parse(self):
        servant_name_links = ['齐格飞', '旅行者']
        res = mooncell.get_all_servants(servant_name_links)
        self.assertEqual(len(res), len(servant_name_links))


if __name__ == '__main__':
    unittest.main()