"""A twisted.web.Resource for the Moon."""

from twisted import web

import moon
import DateTime
import re

TRUE = 1 == 1
FALSE = not TRUE

class MoonResource(web.Resource):
    isLeaf = TRUE
    def render(self, request):
	args = {}

	postpath = request.postpath[:]
	for t in ('year','month','day','hour','minute','second'):
	    if postpath:
		args[t] = postpath.pop(0)
	    else:
		break

	for k in request.args.keys():
	    if request.args[k]:
		args[k] = request.args[k][-1]


	for k in args.keys():
	    try:
		args[k] = int(args[k])
	    except (ValueError, TypeError):
		pass

	if args:
	    date = apply(DateTime.DateTimeFrom,[],args)
	else:
	    date = DateTime.now()

	return self.render_for_date(date)

    def render_for_date(self, date):

	timestring = "%s<br />\nJulian Day Number %d\n" % (
	    date.strftime('%X (at %Z) on<br />\n%A, %d %B,'
                          ' in the year %Y'),
	    date.jdn)

	phase = moon.MoonPhase(date)

	s = "phase: %f<br />\n" \
	    "The moon is %s, %%%.2f full.  (%.1f days old)<br />\n" \
	    "Angular diameter: %.4f&deg;\n" % \
	    (phase.phase,
	     phase.phase_text,
	     phase.illuminated * 100,
	     phase.age,
	     phase.angular_diameter)

        t = """<table border="1">""" \
            """    <tr><th>Phase</th><th>Date</th><th>Days</th></tr>\n"""

        labels = ["New", "1st Quarter", "Full", "3rd Quarter", "New"]
        atts = ['new','q1','full','q3','nextnew']

        for a, label in map(None, atts, labels):
            d = getattr(phase, "%s_date" % a)
            r = """<tr>\n    <td>%s</td><td>%s</td>""" \
                """<td align="right">%.2f</td>\n""" % \
                (label, str(d), d.jdn - phase.date.jdn)
            t = t + r
        t = t + "</table>\n"

	return "<p>%s</p><p>%s</p>\n%s" % (timestring, s, t)
