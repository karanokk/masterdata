import unittest

from masterdata import kazemai


class TestKazemai(unittest.TestCase):
    def test_master_js_id(self):
        js_id = kazemai.master_js_id()
        self.assertIsNotNone(js_id)

    def test__decode_svtcomment(self):
        with open('./testdata/svtcomment_100800', 'rb') as f:
            comment = kazemai._decode_svtcomment(f.read())
            self.assertEqual(len(comment), 7)
            self.assertTrue(isinstance(comment[0], dict))


if __name__ == '__main__':
    unittest.main()
