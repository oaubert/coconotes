from uuid import UUID

from ajax_select import register, LookupChannel
from .models import Video

@register('video')
class VideoLookup(LookupChannel):
    model = Video

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
        return u"<span class='video'>%s</span>" % item.title
