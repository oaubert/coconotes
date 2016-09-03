# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

from .widgets import TimecodeWidget

class AnnotationEditForm(forms.Form):
    begin = forms.FloatField(widget=TimecodeWidget)
    title = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea)
    sharing = forms.ChoiceField()

    class Media:
        css = {
             'all': ('annotation_edit.css',)
         }

    def sharing_choices(self, user):
        return [('private', _("private"))] + \
            [('shared-%s' % group.id, _("shared with %s") % group.name) for group in user.groups.all()]

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
        self.fields['description'].widget.attrs['autofocus'] = ""
        if self.annotation and not self.annotation.title:
            self.fields['title'].widget.attrs['class'] = 'hide_element'

class CommentEditForm(forms.Form):
    title = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea)
    sharing = forms.ChoiceField()
    annotation = forms.HiddenInput()

    class Media:
        css = {
             'all': ('comment_edit.css',)
         }

    def sharing_choices(self, user):
        return [('private', _("private"))] + \
            [('shared-%s' % group.id, _("shared with %s") % group.name) for group in user.groups.all()]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.comment = kwargs.pop('comment')
        super(CommentEditForm, self).__init__(*args, **kwargs)
        # Restrict group field choices to user groups
        self.fields['sharing'].choices = self.sharing_choices(self.user)
        self.fields['description'].widget.attrs['autofocus'] = ""
        if self.comment and not self.comment.title:
            self.fields['title'].widget.attrs['class'] = 'hide_element'

class ConsentEditForm(forms.Form):
    consent = forms.ChoiceField(label="",
                                widget=forms.RadioSelect,
                                choices=[ ('y', "J'accepte de participer à l'étude"),
                                          ('n', "Je refuse que mes données soient utilisées dans le cadre de l'étude") ])
    # 1- Utilisation des réseaux sociaux :
    reseaux_sociaux = forms.MultipleChoiceField(label="Parmi ces réseaux sociaux, lesquels utilisez-vous régulièrement (plus d’une fois par semaine)",
                                                widget=forms.CheckboxSelectMultiple,
                                                choices=[ ('facebook', 'Facebook'),
                                                          ('twitter', 'Twitter'),
                                                          ('instagram', 'Instagram'),
                                                          ('snapchat', 'Snapchat'),
                                                          ('autre', 'Autre') ])

    fb_promo = forms.MultipleChoiceField(label="Utilisez-vous le groupe FB de la promo",
                                         widget=forms.CheckboxSelectMultiple,
                                         choices = [ ('consulter', 'Pour consulter les informations ?'),
                                                     ('ajouter', 'Pour ajouter des  informations ?'),
                                                     ('repondre', 'Pour répondre à des sondages ?'),
                                                     ('non', 'Je n’utilise pas') ])

    # 2- Utilisation des vidéos sur internet
    video_frequence = forms.ChoiceField(label="À quelle fréquence regardez-vous des vidéos sur Internet (Facebook, YouTube, Dailymotion, etc.) ?",
                               choices = [
                                   ('jour', "plusieurs fois par jour"),
                                   ('semaine', "plusieurs fois par semaine"),
                                   ('tempsentemps', "de temps en temps"),
                                   ('rarement', 'rarement')
                               ])

    video_type = forms.MultipleChoiceField(label="Quels types de vidéos regardez-vous généralement sur Internet ?",
                                           widget=forms.CheckboxSelectMultiple,
                                           choices = [
                                               ('aucun', 'Aucun'),
                                               ('musique', 'Vidéo clips musicaux'),
                                               ('docu', 'Documentaires'),
                                               ('actus', 'Actualités'),
                                               ('interviews', 'Interviews de célébrités'),
                                               ('perso', 'Vidéos personnelles (amis, famille)'),
                                               ('streaming', 'Films en streaming'),
                                               ('anime', 'Animations ou dessins animés'),
                                               ('demos', 'Démos de jeux vidéo'),
                                               ('tutoriels', 'Conseils et tutoriels'),
                                               ('enseignement', 'Vidéos d’enseignement '),
                                               ('autres', 'Autres') ])

    video_commentaire = forms.ChoiceField(label="À quelle fréquence commentez-vous des vidéos sur un site de vidéos en ligne ?",
                               choices = [
                                   ('jour', "plusieurs fois par jour"),
                                   ('semaine', "plusieurs fois par semaine"),
                                   ('tempsentemps', "de temps en temps"),
                                   ('jamais', 'jamais')
                               ])
    consent = forms.ChoiceField(label="",
                                widget=forms.RadioSelect,
                                choices=[ ('y', "J'accepte de participer à l'étude"),
                                          ('n', "Je refuse que mes données soient utilisées dans le cadre de l'étude") ])

    video_playlist = forms.ChoiceField(label="Avez-vous réalisé des playlists sur un site de vidéos en ligne ?",
                                       widget=forms.RadioSelect,
                                       choices=[ (True, "Oui"),
                                                 (False, "Non") ])
    video_upload = forms.ChoiceField(label="Avez-vous déjà déposé une vidéo sur un site de vidéos en ligne ?",
                                       widget=forms.RadioSelect,
                                       choices=[ (True, "Oui"),
                                                 (False, "Non") ])
    video_create = forms.ChoiceField(label="Avez-vous déjà réalisé une vidéo ?",
                                       widget=forms.RadioSelect,
                                       choices=[ (True, "Oui"),
                                                 (False, "Non") ])

    class Media:
        css = {
             'all': ('css/consent_edit.css',)
         }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        redirect_to = kwargs.pop('redirect') or '/'
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = "/accounts/profile/consent?next=" + redirect_to
        self.helper.form_class = "consent_edit_form"
        self.helper.layout = Layout(
            Fieldset(
                "<h3>Expression du consentement</h3>",
                "consent"
            ),
            Fieldset(
                "<p>Merci de votre participation. Pour nous permettre d'affiner votre &eacute;tude, merci de prendre le temps de r&eacute;pondre &agrave; quelques questions vous concernant, avant de valider.</p><p></p><h3>Utilisation des r&eacute;seaux sociaux</h3>",
                'reseaux_sociaux',
                'fb_promo',
            ),
            Fieldset(
                "<h3>Utilisation des vid&eacute;os sur internet</h3>",
                'video_frequence',
                'video_type',
                'video_commentaire',
                'video_playlist',
                'video_upload',
                'video_create'
            ),
            Submit('submit', 'Valider', css_class='button white')
        )
        super(ConsentEditForm, self).__init__(*args, **kwargs)
        #self.fields['consent'].initial = self.user.metadata.config.get('consent')
        self.fields['consent'].initial = None
