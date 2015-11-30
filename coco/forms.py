from django.contrib.auth.models import Group
from django import forms
from .models import Annotation

class AnnotationEditForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ('description',
                  'begin', 'end',
                  'group',
                  'visibility')

    def __init__(self, user, *args, **kwargs):
        super(AnnotationEditForm, self).__init__(*args, **kwargs)
        # Restrict group field choices to user groups
        self.fields['group'].queryset = user.groups.all()
