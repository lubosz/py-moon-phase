"""Unit-testing moon.py"""

import moon
import unittest
try:
    import DateTime
except ImportError:
    from mx import DateTime
import math

from types import *

class MoonPhaseConstruction(unittest.TestCase):
    """Test the MoonPhase constructor."""

    def testDefaultConstruction(self):
        o = moon.MoonPhase()

    def testJDNConstruction(self):
        # XXX: Are there any JDN values which should be invalid?
        o = moon.MoonPhase(2452186)

    def testDateTimeConstruction(self):
        o = moon.MoonPhase(DateTime.DateTimeFrom("July 29, 2039"))

    def testBadArgConstruction(self):
        self.assertRaises(TypeError, moon.MoonPhase, "Hoboken")
        self.assertRaises(TypeError, moon.MoonPhase, {})
        self.assertRaises(TypeError, moon.MoonPhase, open)

    def testExtraArgConstruction(self):
        self.assertRaises(TypeError, moon.MoonPhase, 1234567, 4321765)


class MoonPhaseAttributes(unittest.TestCase):
    def setUp(self):
        self.o = moon.MoonPhase()

    def testPresence(self):
        for a in ['date',
                  'phase', 'phase_text', 'illuminated',
                  'angular_diameter', 'sun_angular_diameter',
                  'new_date', 'q1_date',
                  'full_date', 'q3_date', 'nextnew_date']:
            getattr(self.o, a)

    def testAbscence(self):
        self.assertRaises(AttributeError, getattr,
                          self.o, "no_such_attribute")

    # Type checks.
    def testDate(self):
        self.assert_(isinstance(self.o.date, DateTime.DateTimeType))

    def testPhaseText(self):
        self.assert_(self.o.phase_text)
        self.assert_(isinstance(self.o.phase_text, StringType))

    # Range checks.
    def testPhaseRange(self):
        self.assert_(self.o.phase >= 0)
        self.assert_(self.o.phase <= 1)

    def testIlluminatedRange(self):
        self.assert_(self.o.illuminated >= 0)
        self.assert_(self.o.illuminated <= 1)

    def testAgeRange(self):
        self.assert_(self.o.age >= 0)
        self.assert_(self.o.age < 30)

    # Order-of-magnitude checks.
    def testDistanceMagnitude(self):
        self.assert_(5 < math.log10(self.o.distance) < 6)

    def testSunDistanceMagnitude(self):
        self.assert_(8 <= math.log10(self.o.sun_distance) < 9)

    def testAngularDiameterMagnitude(self):
        self.assert_(-0.4 < math.log10(self.o.angular_diameter) < -0.2)

    def testSunAngularDiameterMagnitude(self):
        self.assert_(-0.4 < math.log10(self.o.sun_angular_diameter) < -0.2)


class MoonPhaseAccuracy(unittest.TestCase):
    """Test our output against trusted astronomical data.

    XXX: Obtain data for comparsion!
    """

    # DATA FROM SKY AND TELESCOPE MAGAZINE, UTC:
    lunar_data = [
        ("890107.1922", "new"),
        ("890114.1358", "first"),
        ("890121.2133", "full"),
        ("890130.0202", "last"),
        ("890206.0737", "new"),
        ("890212.2315", "first"),
        ("890220.1532", "full"),
        ("890228.2008", "last"),
        ("890307.1819", "new"),
        ("890314.1011", "first"),
        ("890322.0958", "full"),
        ("890330.1021", "last"),
        ("890406.0333", "new"),
        ("890412.2313", "first"),
        ("890421.0313", "full"),
        ("890428.2046", "last"),
        ("890505.1146", "new"),
        ("890512.1419", "first"),
        ("890520.1816", "full"),
        ("890528.0401", "last"),
        ("890603.1953", "new"),
        ("890611.0659", "first"),
        ("890619.0657", "full"),
        ("890626.0909", "last"),
        ("890703.0459", "new"),
        ("890711.0019", "first"),
        ("890718.1742", "full"),
        ("890725.1331", "last"),
        ("890801.1606", "new"),
        ("890809.1728", "first"),
        ("890817.0307", "full"),
        ("890823.1840", "last"),
        ("890831.0544", "new"),
        ("890908.0949", "first"),
        ("890915.1151", "full"),
        ("890922.0210", "last"),
        ("890929.2147", "new")
        ]

    transtbl = {"new": 0.0,
                "first": 0.25,
                "full": 0.50,
                "last": 0.75}

    tolerance = 0.001

    def testAccuracy(self):
        total_error = 0.0
        for date, phase in self.lunar_data:
            phase = self.transtbl[phase]
            year = 1900 + int(date[0:2])
            month = int(date[2:4])
            day = int(date[4:6])
            hour = int(date[7:9])
            minute = int(date[9:11])

            d = DateTime.DateTimeFrom(year=year,month=month,
                                      day=day,hour=hour,minute=minute)
            o = moon.MoonPhase(d)
            error = abs(phase - o.phase)
            if error > 0.5:
                # phase is circular
                error = 1.0 - error
            total_error = total_error + error

        avg_error = total_error / len(self.lunar_data)
        self.assert_(avg_error < self.tolerance,
                     "avg_error: %s" % avg_error)


class MoonPhaseSeek(unittest.TestCase):
    tolerance = 0.001

    def setUp(self):
        self.o = moon.MoonPhase()
    def testAttibrutePresence(self):
        for p in ['new','q1','full','q3','nextnew']:
            p = "%s_date" % p
            self.assert_(isinstance(getattr(self.o, p),
                                    DateTime.DateTimeType))

    def testBallparkAccuracy(self):
        for p in ['new','q1','full','q3','nextnew']:
            p = "%s_date" % p
            d = getattr(self.o, p)
            if abs(self.o.date.jdn - d.jdn) > 30:
                self.fail("%s more than a month away" % p)

    def testSanityCheck(self):
        phase = 0.0
        for p in ['new','q1','full','q3','nextnew']:
            p = "%s_date" % p
            d = getattr(self.o, p)
            gap = abs(moon.MoonPhase(d).phase - phase)
            if gap > 0.5:
                # How does one test for inequality on a cyclical number
                # line?
                gap = 1 - gap
            self.failUnless(gap < self.tolerance,
                            "Average gap is %s, "\
                            "which exceeds tolerance %s."
                            % (gap, self.tolerance))
            phase = phase + 0.25


if __name__ == "__main__":
    unittest.main()
