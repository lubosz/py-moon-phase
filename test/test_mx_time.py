import unittest
from mx import DateTime


class MxTimeTest(unittest.TestCase):
    def test_construction(self):
        dt = DateTime.DateTime(1900, 1, 1, 12)
        print(dt)


if __name__ == "__main__":
    unittest.main()
