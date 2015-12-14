# -*- coding: utf-8 -*-

import time

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def format_timecode(tc, format="short"):
    """Format a timecode/duration (in seconds)
    """
    if tc is None:
        return '--:--'
    elif tc < 0:
        return '00:00'
    tc = float(tc)
    s = long(tc)
    ms = long(1000 * (tc - s))
    # Format: HH:MM:SS.mmm
    tup = time.gmtime(s)
    if format == 'short':
        if tup.tm_hour > 0:
            return time.strftime("%H:%M:%S", tup)
        else:
            return time.strftime("%M:%S", tup)
    else:
        return "%s.%03d" % (time.strftime("%H:%M:%S", tup), ms)
