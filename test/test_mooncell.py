import unittest
from os.path import exists

from masterdata import kazemai
from masterdata.mooncell import extract, integrator


class TestMooncell(unittest.TestCase):
    def setUp(self):
        path = './jp_masterdata(test).sqlite3'
        if exists(path):
            from masterdata.json2sqlite3 import JSDatabase
            self.db = JSDatabase(path)
        else:
            self.db = kazemai.make_database(path)

    def test_extract(self):
        servant = extract.extract_servants(['齐格飞'])[0]
        print(servant)

    def test_integrate(self):
        servants = extract.extract_servants(
            ['玛修·基列莱特', '宫本武藏', '不夜城的Assassin', '所罗门', 'BeastⅢ／L'])
        self.db.begain()
        ig = integrator.ServantIG(self.db.con, './patch/')
        try:
            for servant in servants:
                ig.integrate(servant)
        finally:
            self.db.rollback()

    def test_a(self):
        import sqlite3
        self.db.con.row_factory = sqlite3.Row
        r = self.db.execute(
            'SELECT *, count(distinct treasureDeviceId) FROM mstSvtTreasureDevice WHERE svtId=100800 AND num=1').fetchone()
        self.db.con.row_factory = None
        print(r)


if __name__ == '__main__':
    unittest.main()
