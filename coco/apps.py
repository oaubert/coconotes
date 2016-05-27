from django.apps import AppConfig
from actstream import registry
from django.contrib.auth.models import User, Group
import coco.signals

class CocoConfig(AppConfig):
    name = 'coco'

    def ready(self):
        for model in ('Channel', 'Chapter', 'Activity',
                      'Video', 'Annotation', 'Comment',
                      'Newsitem'):
            registry.register(self.get_model(model))
        registry.register(User, Group)
