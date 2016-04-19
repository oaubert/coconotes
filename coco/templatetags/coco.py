# -*- coding: utf-8 -*-

import re
import time

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import mark_safe, conditional_escape

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
    try:
        tc = float(tc)
    except ValueError:
        return '--:--'
    s = long(tc)
    ms = long(1000 * (tc - s))
    # Format: HH:MM:SS.mmm
    tup = time.gmtime(s)
    if format == 'short':
        if tup.tm_hour > 0:
            return time.strftime("%H:%M:%S", tup)
        else:
            return time.strftime("%M:%S", tup)
    elif format == 'ms':
        if tup.tm_hour > 0:
            return "%s.%03d" % (time.strftime("%H:%M:%S", tup), ms)
        else:
            return "%s.%03d" % (time.strftime("%M:%S", tup), ms)
    else:
        return "%s.%03d" % (time.strftime("%H:%M:%S", tup), ms)

small_time_regexp=re.compile('(?P<m>\d+):(?P<s>\d+)(?P<sep>[.,]?)(?P<ms>\d+)?$')
time_regexp=re.compile('(?P<h>\d+):(?P<m>\d+):(?P<s>\d+)(?P<sep>[.,]?)(?P<ms>\d+)?$')
@register.filter
def parse_timecode(s):
    """Parse a string timecode representation into a float.

    This function tries to handle multiple formats:

    - plain integers are considered as milliseconds.
      Regexp: \d+
      Example: 2134 or 134 or 2000

    - float numbers are considered as seconds
      Regexp: \d*\.\d*
      Example: 2.134 or .134 or 2.

    - formatted timestamps with colons in them will be interpreted as follows.
      m:s (1 colon)
      m:s.ms (1 colon)
      m:sfNN
      h:m:s (2 colons)
      h:m:s.ms (2 colons)
      h:m:sfNN

      Legend:
      h: hours
      m: minutes
      s: seconds
      ms: milliseconds
      NN: frame number
    """
    try:
        tc = float(s)
    except ValueError:
        # It was not a plain float. Try to determine its format.
        t = None
        m = time_regexp.match(s)
        if m:
            t = m.groupdict()
        else:
            m = small_time_regexp.match(s)
            if m:
                t = m.groupdict()
                t['h'] = 0

        if t is not None:
            if 'ms' in t and t['ms']:
                t['ms']=(t['ms'] + ("0" * 4))[:3]
            else:
                t['ms']=0
            for k in t:
                if t[k] is None:
                    t[k] = 0
                try:
                    t[k] = long(t[k] or 0)
                except ValueError:
                    t[k] = 0
            tc = t.get('ms', 0) / 1000. + t.get('s', 0) + t.get('m', 0) * 60 + t.get('h', 0) * 3600
        else:
            raise ValueError("Unknown time format for %s" % s)
    return tc

@register.filter(needs_autoescape=True)
@stringfilter
def term_highlight(text, searched_term="", autoescape=None):
    """Highlight term.
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    pattern = re.compile('(%s)' % esc(searched_term), re.IGNORECASE)
    (result, count) = pattern.subn(r'<mark class="snippet_highlight">\1</mark>', esc(unicode(text)))
    return mark_safe(result)

@register.filter
def get_item(container, key):
    if type(container) is dict:
        return container.get(key)
    elif type(container) in (list, tuple):
        return container[key] if len(container) > key else None
    return None
