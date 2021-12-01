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


# DATA FROM SKY AND TELESCOPE MAGAZINE, UTC:
LUNAR_DATA = [
    (datetime(1989, 1, 7, 19, 22), NEW_MOON),
    (datetime(1989, 1, 14, 13, 58), FIRST_QUARTER),
    (datetime(1989, 1, 21, 21, 33), FULL_MOON),
    (datetime(1989, 1, 30, 2, 2), LAST_QUARTER),
    (datetime(1989, 2, 6, 7, 37), NEW_MOON),
    (datetime(1989, 2, 12, 23, 15), FIRST_QUARTER),
    (datetime(1989, 2, 20, 15, 32), FULL_MOON),
    (datetime(1989, 2, 28, 20, 8), LAST_QUARTER),
    (datetime(1989, 3, 7, 18, 19), NEW_MOON),
    (datetime(1989, 3, 14, 10, 11), FIRST_QUARTER),
    (datetime(1989, 3, 22, 9, 58), FULL_MOON),
    (datetime(1989, 3, 30, 10, 21), LAST_QUARTER),
    (datetime(1989, 4, 6, 3, 33), NEW_MOON),
    (datetime(1989, 4, 12, 23, 13), FIRST_QUARTER),
    (datetime(1989, 4, 21, 3, 13), FULL_MOON),
    (datetime(1989, 4, 28, 20, 46), LAST_QUARTER),
    (datetime(1989, 5, 5, 11, 46), NEW_MOON),
    (datetime(1989, 5, 12, 14, 19), FIRST_QUARTER),
    (datetime(1989, 5, 20, 18, 16), FULL_MOON),
    (datetime(1989, 5, 28, 4, 1), LAST_QUARTER),
    (datetime(1989, 6, 3, 19, 53), NEW_MOON),
    (datetime(1989, 6, 11, 6, 59), FIRST_QUARTER),
    (datetime(1989, 6, 19, 6, 57), FULL_MOON),
    (datetime(1989, 6, 26, 9, 9), LAST_QUARTER),
    (datetime(1989, 7, 3, 4, 59), NEW_MOON),
    (datetime(1989, 7, 11, 0, 19), FIRST_QUARTER),
    (datetime(1989, 7, 18, 17, 42), FULL_MOON),
    (datetime(1989, 7, 25, 13, 31), LAST_QUARTER),
    (datetime(1989, 8, 1, 16, 6), NEW_MOON),
    (datetime(1989, 8, 9, 17, 28), FIRST_QUARTER),
    (datetime(1989, 8, 17, 3, 7), FULL_MOON),
    (datetime(1989, 8, 23, 18, 40), LAST_QUARTER),
    (datetime(1989, 8, 31, 5, 44), NEW_MOON),
    (datetime(1989, 9, 8, 9, 49), FIRST_QUARTER),
    (datetime(1989, 9, 15, 11, 51), FULL_MOON),
    (datetime(1989, 9, 22, 2, 10), LAST_QUARTER),
    (datetime(1989, 9, 29, 21, 47), NEW_MOON),
]


class MoonPhaseAccuracy(unittest.TestCase):
    """Test output against trusted astronomical data."""

    tolerance = 0.001

    def testAccuracy(self):
        total_error = 0.0
        for dt, phase in LUNAR_DATA:
            o = moon.MoonPhase(dt)
            error = abs(phase - o.phase)
            if error > 0.5:
                # phase is circular
                error = 1.0 - error
            total_error = total_error + error

        avg_error = total_error / len(LUNAR_DATA)
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
