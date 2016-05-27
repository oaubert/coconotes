from django.db.models.signals import pre_save, post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Annotation, VISIBILITY_PUBLIC, VISIBILITY_GROUP
from actstream import action

@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
    action.send(request.user, verb="loggedin")

@receiver(user_logged_out)
def sig_user_logged_out(sender, user, request, **kwargs):
    action.send(request.user, verb="loggedout")

@receiver(pre_save, sender=Annotation)
def sig_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
        # Cannot do
        # action.send(instance.creator, verb="created", action_object=instance)
        # here, see sig_post_save
    else:
        if old.visibility != instance.visibility:
            if instance.visibility == VISIBILITY_PUBLIC:
                action.send(instance.contributor, verb="published", action_object=instance)
            elif instance.visibility == VISIBILITY_GROUP:
                action.send(instance.contributor, verb="shared", action_object=instance, target=instance.group)
            else:
                action.send(instance.contributor, verb="unshared", action_object=instance)
        if old.title != instance.title or old.description != instance.description:
            action.send(instance.contributor, verb="updated", action_object=instance)


@receiver(post_save, sender=Annotation)
def sig_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        # This cannot be set in pre_save, since the object instance is not yet saved to the DB
        action.send(instance.contributor, verb="created", action_object=instance)
