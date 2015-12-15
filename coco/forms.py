from django import forms
from django.utils.translation import ugettext as _


class AnnotationEditForm(forms.Form):
    begin = forms.FloatField()
    description = forms.CharField(widget=forms.Textarea)
    sharing = forms.ChoiceField()

    class Media:
        css = {
             'all': ('annotation_edit.css',)
         }

    def sharing_choices(self, user):
        return [('private', _("private"))] + \
            [('shared-%s' % group.id, _("shared with %s") % group.name) for group in user.groups.all()] + \
            [('public', _("public"))]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.annotation = kwargs.pop('annotation')
        super(AnnotationEditForm, self).__init__(*args, **kwargs)
        self.fields['begin'].min_value = 0
        if self.annotation is not None:
            self.fields['begin'].max_value = self.annotation.video.duration
        # self.fields['begin'].max_value = [video].duration
        # Restrict group field choices to user groups
        self.fields['sharing'].choices = self.sharing_choices(self.user)
