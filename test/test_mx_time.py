import unittest
from mx import DateTime
from IPython import embed
from datetime import datetime
import time

class MxTimeTest(unittest.TestCase):
    def test_construction(self):
        dt = DateTime.DateTime(1900, 1, 1, 12)
        print(dt)

        now = DateTime.now()
        print(now)

        # embed()

        print("Abs days", now.absdays)
        print("Abs time", now.abstime)

        print("ticks", now.ticks())

        print("gm ticks", now.gmticks())

        dt_now = datetime.now()
        print("dt now", dt_now)

        dt_utc_now = datetime.utcnow()
        print("dt utc now", dt_utc_now)

        now_unix = time.time()
        print("time.time", now_unix)

        dt_utc_from_ts = datetime.utcfromtimestamp(now_unix)
        print(dt_utc_from_ts)

        mx_gmtime = DateTime.now().gmtime()
        print("mx_gmtime", mx_gmtime.gmticks())


if __name__ == "__main__":
    unittest.main()
