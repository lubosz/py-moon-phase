import unittest
import calendar

from mx import DateTime
from datetime import datetime, tzinfo, timedelta
import time


class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)


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

    def test_utc(self):
        dt_mx = DateTime.DateTimeFrom("July 29, 2039")
        print("dt_mx unix", dt_mx.ticks())
        print("dt_mx unixgm", dt_mx.gmticks())

        dt = datetime(2039, 7, 29, tzinfo=UTC())
        dt_unix = time.mktime(dt.timetuple())
        print("dt unix", dt_unix)

        dt_local = datetime(2039, 7, 29)
        dt_utc_unix = calendar.timegm(dt_local.timetuple())
        # print("dt_local timetuple", dt_local.timetuple())
        print("dt utc unix", dt_utc_unix)

        dt_utc_unix = calendar.timegm((2039, 7, 29, 0, 0, 0))
        print("dt utc unix 2", dt_utc_unix)

        # print("dt_local gmtime", time.gmtime(dt_local_unix))
        # print("dt_local localtime", time.localtime(dt_local_unix))

        dt_mx_from_unix = DateTime.gmtime(2195510400)
        print(dt_mx_from_unix)

        print("time.gmtime(2195510400)", time.gmtime(2195510400))

        d = DateTime.DateTimeFrom(year=2039, month=7, day=29)
        print("dt_mx unix2", d.ticks())


if __name__ == "__main__":
    unittest.main()
