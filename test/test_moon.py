"""Unit-testing moon.py"""

import moon
import unittest

import math
from datetime import datetime


class MoonPhaseConstruction(unittest.TestCase):
    """Test the MoonPhase constructor."""

    def testDefaultConstruction(self):
        moon.MoonPhase()

    def testDateTimeConstruction(self):
        moon.MoonPhase(datetime(2039, 7, 29))

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
        self.assertTrue(isinstance(self.o.date, datetime))

    def testPhaseText(self):
        self.assertTrue(self.o.phase_text)
        self.assertTrue(isinstance(self.o.phase_text, str))

    # Range checks.
    def testPhaseRange(self):
        self.assertTrue(self.o.phase >= 0)
        self.assertTrue(self.o.phase <= 1)

    def testIlluminatedRange(self):
        self.assertTrue(self.o.illuminated >= 0)
        self.assertTrue(self.o.illuminated <= 1)

    def testAgeRange(self):
        self.assertTrue(self.o.age >= 0)
        self.assertTrue(self.o.age < 30)

    # Order-of-magnitude checks.
    def testDistanceMagnitude(self):
        self.assertTrue(5 < math.log10(self.o.distance) < 6)

    def testSunDistanceMagnitude(self):
        self.assertTrue(8 <= math.log10(self.o.sun_distance) < 9)

    def testAngularDiameterMagnitude(self):
        self.assertTrue(-0.4 < math.log10(self.o.angular_diameter) < -0.2)

    def testSunAngularDiameterMagnitude(self):
        self.assertTrue(-0.4 < math.log10(self.o.sun_angular_diameter) < -0.2)


NEW_MOON = 0.0
FIRST_QUARTER = 0.25
FULL_MOON = 0.5
LAST_QUARTER = 0.75


class MoonPhaseAccuracy(unittest.TestCase):
    """Test our output against trusted astronomical data.

    XXX: Obtain data for comparsion!
    """

    # DATA FROM SKY AND TELESCOPE MAGAZINE, UTC:
    lunar_data = [
        ("890107.1922", NEW_MOON),
        ("890114.1358", FIRST_QUARTER),
        ("890121.2133", FULL_MOON),
        ("890130.0202", LAST_QUARTER),
        ("890206.0737", NEW_MOON),
        ("890212.2315", FIRST_QUARTER),
        ("890220.1532", FULL_MOON),
        ("890228.2008", LAST_QUARTER),
        ("890307.1819", NEW_MOON),
        ("890314.1011", FIRST_QUARTER),
        ("890322.0958", FULL_MOON),
        ("890330.1021", LAST_QUARTER),
        ("890406.0333", NEW_MOON),
        ("890412.2313", FIRST_QUARTER),
        ("890421.0313", FULL_MOON),
        ("890428.2046", LAST_QUARTER),
        ("890505.1146", NEW_MOON),
        ("890512.1419", FIRST_QUARTER),
        ("890520.1816", FULL_MOON),
        ("890528.0401", LAST_QUARTER),
        ("890603.1953", NEW_MOON),
        ("890611.0659", FIRST_QUARTER),
        ("890619.0657", FULL_MOON),
        ("890626.0909", LAST_QUARTER),
        ("890703.0459", NEW_MOON),
        ("890711.0019", FIRST_QUARTER),
        ("890718.1742", FULL_MOON),
        ("890725.1331", LAST_QUARTER),
        ("890801.1606", NEW_MOON),
        ("890809.1728", FIRST_QUARTER),
        ("890817.0307", FULL_MOON),
        ("890823.1840", LAST_QUARTER),
        ("890831.0544", NEW_MOON),
        ("890908.0949", FIRST_QUARTER),
        ("890915.1151", FULL_MOON),
        ("890922.0210", LAST_QUARTER),
        ("890929.2147", NEW_MOON)
    ]

    tolerance = 0.001

    def testAccuracy(self):
        total_error = 0.0
        for date, phase in self.lunar_data:
            year = 1900 + int(date[0:2])
            month = int(date[2:4])
            day = int(date[4:6])
            hour = int(date[7:9])
            minute = int(date[9:11])

            d = datetime(year, month, day, hour, minute)
            o = moon.MoonPhase(d)
            error = abs(phase - o.phase)
            if error > 0.5:
                # phase is circular
                error = 1.0 - error
            total_error = total_error + error

        avg_error = total_error / len(self.lunar_data)
        self.assertTrue(avg_error < self.tolerance,
                        "avg_error: %s" % avg_error)


class MoonPhaseSeek(unittest.TestCase):
    tolerance = 0.001

    def setUp(self):
        self.o = moon.MoonPhase()

    def testAttibrutePresence(self):
        for p in ['new', 'q1', 'full', 'q3', 'nextnew']:
            self.assertTrue(isinstance(getattr(self.o, f"{p}_date"), datetime))

    def testBallparkAccuracy(self):
        for p in ['new', 'q1', 'full', 'q3', 'nextnew']:
            dt = getattr(self.o, f"{p}_date")
            if abs(moon.datetime_to_julian_days(self.o.date) - moon.datetime_to_julian_days(dt)) > 30:
                self.fail("%s more than a month away" % p)

    def testSanityCheck(self):
        phase = 0.0
        for p in ['new', 'q1', 'full', 'q3', 'nextnew']:
            dt = getattr(self.o, f"{p}_date")
            gap = abs(moon.MoonPhase(dt).phase - phase)
            if gap > 0.5:
                # How does one test for inequality on a cyclical number
                # line?
                gap = 1 - gap
            self.assertTrue(gap < self.tolerance,
                            "Average gap is %s, which exceeds tolerance %s."
                            % (gap, self.tolerance))
            phase = phase + 0.25


if __name__ == "__main__":
    unittest.main()
