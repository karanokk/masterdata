import unittest

from masterdata import mooncell


class TestMooncell(unittest.TestCase):
    def test_get_servant_name_links(self):
        names = mooncell.extract.get_servant_name_links()
        self.assertEqual(names[0], '玛修·基列莱特')


if __name__ == '__main__':
    unittest.main()
