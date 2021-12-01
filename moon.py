#!/usr/bin/env python3
# moon.py, based on code by John Walker (http://www.fourmilab.ch/)
# ported to Python by Kevin Turner <acapnotic@twistedmatrix.com>
# on June 6, 2001 (JDN 2452066.52491), under a full moon.
#
# This program is in the public domain: "Do what thou wilt shall be
# the whole of the law".

"""Functions to find the phase of the moon.

Ported from \"A Moon for the Sun\" (aka moontool.c), a program by the
venerable John Walker.  He used algoritms from \"Practical Astronomy
With Your Calculator\" by Peter Duffett-Smith, Second Edition.

For the full history of the code, as well as references to other
reading material and other entertainments, please refer to John
Walker's website,
http://www.fourmilab.ch/
(Look under the Science/Astronomy and Space heading.)

The functions of primary interest provided by this module are phase(),
which gives you a variety of data on the status of the moon for a
given date; and phase_hunt(), which given a date, finds the dates of
the nearest full moon, new moon, etc.
"""
import math
from math import sin, cos, floor, sqrt, tan, atan
import bisect
from datetime import datetime, timedelta


def datetime_to_days(dt):
    delta = dt - datetime(1, 1, 1)
    return delta.total_seconds() / (60 * 60 * 24)


def datetime_to_julian_days(dt):
    return datetime_to_days(dt) + 1721424.5 + 1


def julian_days_to_datetime(julian_days):
    days = julian_days - (1721424.5 + 1)
    seconds = days * (60 * 60 * 24)
    return datetime(1, 1, 1) + timedelta(seconds=seconds)


__TODO__ = [
    'Add command-line interface.',
    'Make front-end modules for ASCII and various GUIs.',
]

# Precision used when describing the moon's phase in textual format,
# in phase_string().
PRECISION = 0.05
NEW_MOON = 0.0
FIRST_QUARTER = 0.25
FULL_MOON = 0.5
LAST_QUARTER = 0.75
NEXT_NEW = 1.0


class MoonPhase:
    """I describe the phase of the moon.

    I have the following properties:
        date - a DateTime instance
        phase - my phase, in the range 0.0 .. 1.0
        phase_text - a string describing my phase
        illuminated - the percentage of the face of the moon illuminated
        angular_diameter - as seen from Earth, in degrees.
        sun_angular_diameter - as seen from Earth, in degrees.

        new_date - the date of the most recent new moon
        q1_date - the date the moon reaches 1st quarter in this cycle
        full_date - the date of the full moon in this cycle
        q3_date - the date the moon reaches 3rd quarter in this cycle
        nextnew_date - the date of the next new moon
    """

    def __init__(self, date=datetime.utcnow()):
        """MoonPhase constructor.

        Give me a date, as DateTime object."""
        self.date = date

        self.__dict__.update(phase(self.date))

        self.phase_text = phase_string(self.phase)

    def __getattr__(self, a):
        if a in ['new_date', 'q1_date', 'full_date', 'q3_date',
                 'nextnew_date']:
            (self.new_date, self.q1_date, self.full_date,
             self.q3_date, self.nextnew_date) = phase_hunt(self.date)

            return getattr(self, a)
        raise AttributeError(a)

    def __repr__(self):
        jdn = datetime_to_julian_days(self.date)

        return "<%s(%d)>" % (self.__class__, jdn)

    def __str__(self):
        d = self.date
        return "%s for %s, %s (%%%.2f illuminated)" % \
               (self.__class__, d.__str__, self.phase_text,
                self.illuminated * 100)


# JDN stands for Julian Day Number
# Angles here are in degrees

# 1980 January 0.0 in JDN
# XXX: DateTime(1980).jdn yields 2444239.5 -- which one is right?
EPOCH = 2444238.5

# Ecliptic longitude of the Sun at epoch 1980.0
ECLIPTIC_LONGITUDE_EPOCH = 278.833540

# Ecliptic longitude of the Sun at perigee
ECLIPTIC_LONGITUDE_PERIGEE = 282.596403

# Eccentricity of Earth's orbit
ECCENTRICITY = 0.016718

# Semi-major axis of Earth's orbit, in kilometers
SUN_SMAXIS = 1.49585e8

# Sun's angular size, in degrees, at semi-major axis distance
SUN_ANGULAR_SIZE_SMAXIS = 0.533128

# Elements of the Moon's orbit, epoch 1980.0

# Moon's mean longitude at the epoch
MOON_MEAN_LONGITUDE_EPOCH = 64.975464
# Mean longitude of the perigee at the epoch
MOON_MEAN_PERIGEE_EPOCH = 349.383063

# Mean longitude of the node at the epoch
NODE_MEAN_LONGITUDE_EPOCH = 151.950429

# Inclination of the Moon's orbit
MOON_INCLINATION = 5.145396

# Eccentricity of the Moon's orbit
MOON_ECCENTRICITY = 0.054900

# Moon's angular size at distance a from Earth
MOON_ANGULAR_SIZE = 0.5181

# Semi-mojor axis of the Moon's orbit, in kilometers
MOON_SMAXIS = 384401.0
# Parallax at a distance a from Earth
MOON_PARALLAX = 0.9507

# Synodic month (new Moon to new Moon), in days
SYNODIC_MONTH = 29.53058868

# Base date for E. W. Brown's numbered series of lunations (1923 January 16)
LUNATIONS_BASE = 2423436.0

# Properties of the Earth
EARTH_RADIUS = 6378.16


# Little handy mathematical functions.
def norm_angle(angle: float) -> float:
    return angle % 360.0


def dsin(d):
    return sin(math.radians(d))


def dcos(d):
    return cos(math.radians(d))


def phase_string(p):
    phase_strings = (
        (NEW_MOON + PRECISION, "new"),
        (FIRST_QUARTER - PRECISION, "waxing crescent"),
        (FIRST_QUARTER + PRECISION, "first quarter"),
        (FULL_MOON - PRECISION, "waxing gibbous"),
        (FULL_MOON + PRECISION, "full"),
        (LAST_QUARTER - PRECISION, "waning gibbous"),
        (LAST_QUARTER + PRECISION, "last quarter"),
        (NEXT_NEW - PRECISION, "waning crescent"),
        (NEXT_NEW + PRECISION, "new"))

    i = bisect.bisect([a[0] for a in phase_strings], p)

    return phase_strings[i][1]


def phase(phase_date=datetime.utcnow()):
    """Calculate phase of moon as a fraction:

    The argument is the time for which the phase is requested,
    expressed in either a DateTime or by Julian Day Number.

    Returns a dictionary containing the terminator phase angle as a
    percentage of a full circle (i.e., 0 to 1), the illuminated
    fraction of the Moon's disc, the Moon's age in days and fraction,
    the distance of the Moon from the centre of the Earth, and the
    angular diameter subtended by the Moon as seen by an observer at
    the centre of the Earth."""

    # Calculation of the Sun's position

    # date within the epoch
    day = datetime_to_julian_days(phase_date) - EPOCH

    # Mean anomaly of the Sun
    N = norm_angle((360 / 365.2422) * day)
    # Convert from perigee coordinates to epoch 1980
    M = norm_angle(N + ECLIPTIC_LONGITUDE_EPOCH - ECLIPTIC_LONGITUDE_PERIGEE)

    # Solve Kepler's equation
    Ec = kepler(M, ECCENTRICITY)
    Ec = sqrt((1 + ECCENTRICITY) / (1 - ECCENTRICITY)) * tan(Ec / 2.0)
    # True anomaly
    Ec = 2 * math.degrees(atan(Ec))
    # Sun's geometric ecliptic longitude
    lambda_sun = norm_angle(Ec + ECLIPTIC_LONGITUDE_PERIGEE)

    # Orbital distance factor
    F = ((1 + ECCENTRICITY * cos(math.radians(Ec))) / (1 - ECCENTRICITY ** 2))

    # Distance to Sun in km
    sun_dist = SUN_SMAXIS / F
    sun_angular_diameter = F * SUN_ANGULAR_SIZE_SMAXIS

    ########
    #
    # Calculation of the Moon's position

    # Moon's mean longitude
    moon_longitude = norm_angle(13.1763966 * day + MOON_MEAN_LONGITUDE_EPOCH)

    # Moon's mean anomaly
    MM = norm_angle(moon_longitude - 0.1114041 * day - MOON_MEAN_PERIGEE_EPOCH)

    # Moon's ascending node mean longitude
    # MN = norm_angle(c.node_mean_longitude_epoch - 0.0529539 * day)

    evection = 1.2739 * sin(math.radians(2 * (moon_longitude - lambda_sun) - MM))

    # Annual equation
    annual_eq = 0.1858 * sin(math.radians(M))

    # Correction term
    A3 = 0.37 * sin(math.radians(M))

    MmP = MM + evection - annual_eq - A3

    # Correction for the equation of the centre
    mEc = 6.2886 * sin(math.radians(MmP))

    # Another correction term
    A4 = 0.214 * sin(math.radians(2 * MmP))

    # Corrected longitude
    lP = moon_longitude + evection + mEc - annual_eq + A4

    # Variation
    variation = 0.6583 * sin(math.radians(2 * (lP - lambda_sun)))

    # True longitude
    lPP = lP + variation

    #
    # Calculation of the Moon's inclination
    # unused for phase calculation.

    # Corrected longitude of the node
    # NP = MN - 0.16 * sin(torad(M))

    # Y inclination coordinate
    # y = sin(torad(lPP - NP)) * cos(torad(c.moon_inclination))

    # X inclination coordinate
    # x = cos(torad(lPP - NP))

    # Ecliptic longitude (unused?)
    # lambda_moon = todeg(atan2(y,x)) + NP

    # Ecliptic latitude (unused?)
    # BetaM = todeg(asin(sin(torad(lPP - NP)) * sin(torad(c.moon_inclination))))

    #######
    #
    # Calculation of the phase of the Moon

    # Age of the Moon, in degrees
    moon_age = lPP - lambda_sun

    # Phase of the Moon
    moon_phase = (1 - cos(math.radians(moon_age))) / 2.0

    # Calculate distance of Moon from the centre of the Earth
    moon_dist = (MOON_SMAXIS * (1 - MOON_ECCENTRICITY ** 2)) / (1 + MOON_ECCENTRICITY * cos(math.radians(MmP + mEc)))

    # Calculate Moon's angular diameter
    moon_diam_frac = moon_dist / MOON_SMAXIS
    moon_angular_diameter = MOON_ANGULAR_SIZE / moon_diam_frac

    # Calculate Moon's parallax (unused?)
    # moon_parallax = c.moon_parallax / moon_diam_frac

    res = {
        'phase': norm_angle(moon_age) / 360.0,
        'illuminated': moon_phase,
        'age': SYNODIC_MONTH * norm_angle(moon_age) / 360.0,
        'distance': moon_dist,
        'angular_diameter': moon_angular_diameter,
        'sun_distance': sun_dist,
        'sun_angular_diameter': sun_angular_diameter
    }

    return res


def phase_hunt(sdate=datetime.utcnow()):
    """Find time of phases of the moon which surround the current date.

    Five phases are found, starting and ending with the new moons
    which bound the current lunation.
    """

    adate = sdate - timedelta(days=45)

    k1 = floor((adate.year + ((adate.month - 1) * (1.0 / 12.0)) - 1900) * 12.3685)

    nt1 = mean_phase(adate, k1)
    adate_0 = nt1

    while True:
        adate_0 += SYNODIC_MONTH
        k2 = k1 + 1
        nt2 = mean_phase(julian_days_to_datetime(adate_0), k2)
        if nt1 <= datetime_to_julian_days(sdate) < nt2:
            break
        nt1 = nt2
        k1 = k2

    phases = list(map(true_phase,
                      [k1, k1, k1, k1, k2],
                      [0 / 4.0, 1 / 4.0, 2 / 4.0, 3 / 4.0, 0 / 4.0]))

    return phases


def mean_phase(sdate, k):
    """Calculates time of the mean new Moon for a given base date.

    This argument K to this function is the precomputed synodic month
    index, given by:

                        K = (year - 1900) * 12.3685

    where year is expressed as a year and fractional year.
    """

    # Time in Julian centuries from 1900 January 0.5
    delta_t = sdate - datetime(1900, 1, 1, 12)
    t = delta_t.days / 36525

    # square for frequent use
    t2 = t * t
    # and cube
    t3 = t2 * t

    nt1 = (
            2415020.75933 + SYNODIC_MONTH * k + 0.0001178 * t2 -
            0.000000155 * t3 + 0.00033 * dsin(166.56 + 132.87 * t -
                                              0.009173 * t2)
    )

    return nt1


def true_phase(k, tphase):
    """Given a K value used to determine the mean phase of the new
    moon, and a phase selector (0.0, 0.25, 0.5, 0.75), obtain the
    true, corrected phase time."""

    apcor = False

    # add phase to new moon time
    k = k + tphase
    # Time in Julian centuries from 1900 January 0.5
    t = k / 1236.85

    t2 = t * t
    t3 = t2 * t

    # Mean time of phase
    pt = (
            2415020.75933 + SYNODIC_MONTH * k + 0.0001178 * t2 -
            0.000000155 * t3 + 0.00033 * dsin(166.56 + 132.87 * t -
                                              0.009173 * t2)
    )

    # Sun's mean anomaly
    m = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3

    # Moon's mean anomaly
    mprime = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3

    # Moon's argument of latitude
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3

    if (tphase < 0.01) or (abs(tphase - 0.5) < 0.01):

        # Corrections for New and Full Moon
        pt = pt + (
                (0.1734 - 0.000393 * t) * dsin(m)
                + 0.0021 * dsin(2 * m)
                - 0.4068 * dsin(mprime)
                + 0.0161 * dsin(2 * mprime)
                - 0.0004 * dsin(3 * mprime)
                + 0.0104 * dsin(2 * f)
                - 0.0051 * dsin(m + mprime)
                - 0.0074 * dsin(m - mprime)
                + 0.0004 * dsin(2 * f + m)
                - 0.0004 * dsin(2 * f - m)
                - 0.0006 * dsin(2 * f + mprime)
                + 0.0010 * dsin(2 * f - mprime)
                + 0.0005 * dsin(m + 2 * mprime)
        )

        apcor = True
    elif (abs(tphase - 0.25) < 0.01) or (abs(tphase - 0.75) < 0.01):

        pt = pt + (
                (0.1721 - 0.0004 * t) * dsin(m)
                + 0.0021 * dsin(2 * m)
                - 0.6280 * dsin(mprime)
                + 0.0089 * dsin(2 * mprime)
                - 0.0004 * dsin(3 * mprime)
                + 0.0079 * dsin(2 * f)
                - 0.0119 * dsin(m + mprime)
                - 0.0047 * dsin(m - mprime)
                + 0.0003 * dsin(2 * f + m)
                - 0.0004 * dsin(2 * f - m)
                - 0.0006 * dsin(2 * f + mprime)
                + 0.0021 * dsin(2 * f - mprime)
                + 0.0003 * dsin(m + 2 * mprime)
                + 0.0004 * dsin(m - 2 * mprime)
                - 0.0003 * dsin(2 * m + mprime)
        )
        if tphase < 0.5:
            #  First quarter correction
            pt = pt + 0.0028 - 0.0004 * dcos(m) + 0.0003 * dcos(mprime)
        else:
            #  Last quarter correction
            pt = pt + -0.0028 + 0.0004 * dcos(m) - 0.0003 * dcos(mprime)
        apcor = True

    if not apcor:
        raise ValueError(
            "TRUEPHASE called with invalid phase selector",
            tphase)

    return julian_days_to_datetime(pt)


def kepler(m, ecc):
    """Solve the equation of Kepler."""

    epsilon = 1e-6

    m = math.radians(m)
    e = m
    while 1:
        delta = e - ecc * sin(e) - m
        e = e - delta / (1.0 - ecc * cos(e))

        if abs(delta) <= epsilon:
            break

    return e


def main():
    m = MoonPhase()
    s = """The moon is %s, %.1f%% illuminated, %.1f days old.""" % \
        (m.phase_text, m.illuminated * 100, m.age)
    print(s)


if __name__ == '__main__':
    main()
