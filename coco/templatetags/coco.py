# -*- coding: utf-8 -*-

import time

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def format_timecode(tc):
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
    return "%s.%03d" % (time.strftime("%H:%M:%S", time.gmtime(s)), ms)
