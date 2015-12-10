from ajax_select import register, LookupChannel
from .models import Video, Chapter, Activity, Channel
from django.contrib.auth.models import User, Group


class ElementLookup(LookupChannel):
    """Generic lookup method against fields
    """
    def get_objects(self, ids):
        """Get objects.

        Reimplement the original method, the original return line does
        not function correctly with UUIDs
        """
        pk_type = self.model._meta.pk.to_python
        ids = [pk_type(pk) for pk in ids]
        things = self.model.objects.in_bulk(ids)
        return things.values()

    def get_query(self, q, request):
        return self.model.objects.filter(title__icontains=q).order_by('title')[:20]

    def format_item_display(self, item):
        return u'<span class="%s_lookup">%s</span>' % (self.model._meta.model_name, item.title)


@register('video')
class VideoLookup(ElementLookup):
    model = Video


@register('chapter')
class ChapterLookup(ElementLookup):
    model = Chapter


@register('activity')
class ActivityLookup(ElementLookup):
    model = Activity


@register('channel')
class ChannelLookup(ElementLookup):
    model = Channel


@register('user')
class UserLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        return self.model.objects.filter(username__icontains=q).order_by('username')[:20]

    def format_item_display(self, item):
        return u'<span class="user_lookup">%s</span>' % item.username


@register('group')
class GroupLookup(LookupChannel):
    model = Group

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')[:20]

    def format_item_display(self, item):
        return u'<span class="group_lookup">%s</span>' % item.name
