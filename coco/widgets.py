from django import forms

from .templatetags.coco import format_timecode, parse_timecode

class TimecodeWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})['size'] = 8
        super(TimecodeWidget, self).__init__(*args, **kwargs)

    def _format_value(self, value):
        return format_timecode(value)

    def to_python(self, value):
        try:
            t = parse_timecode(value)
        except ValueError:
            t = 0
        return t

#    class Media:
#        js = ('static/js/timecode-widget.js',)
