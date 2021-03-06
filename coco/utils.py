import re

from actstream import action

from django.db.models import Q
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType

# Generic search code from https://github.com/squarepegsys/django-simple-search/
# Interim code, to be removed after solr integration


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def build_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})

            if or_query:
                or_query = or_query | q
            else:
                or_query = q

        if query:
            query = query & or_query
        else:
            query = or_query
    return query


def generic_search(request, model, fields, query_param="q"):
    """
    """
    query_string = request.GET.get(query_param, "").strip()
    if not query_string:
        return model.objects.all()

    entry_query = build_query(query_string, fields)
    try:
        model.annotationtype
        prefetch_related = ('creator', 'contributor', 'annotationtype')
    except AttributeError:
        prefetch_related = ('creator', 'contributor')
    found_entries = model.objects.prefetch_related(*prefetch_related).filter(entry_query)
    return found_entries


ACTION = {
    'addition': ADDITION,
    'change': CHANGE,
    'deletion': DELETION
}
def update_object_history(request, obj, action='change', message=None):
    """Update object history.
    action is a string: addition, change, deletion
    """
    if not message:
        message =  '%s of %s' % (unicode(obj), action)
    LogEntry.objects.log_action(
        user_id         = request.user.pk,
        content_type_id = ContentType.objects.get_for_model(obj).pk,
        object_id       = obj.pk,
        object_repr     = unicode(obj),
        action_flag     = ACTION[action],
        change_message  = message
    )

def log_access(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            action.send(request.user, verb='accessed', url=request.path)
        return func(request, *args, **kwargs)
    return wrapper
