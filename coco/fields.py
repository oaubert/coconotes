from django.db.models import SlugField

# From http://stackoverflow.com/questions/21728500/optional-but-unique-slugfield
# Inspired by: https://github.com/django-extensions/django-extensions/blob/master/django_extensions/db/fields/__init__.py
class SlugOrNullField(SlugField):
    """Don't insert empty slugs. If the slug is empty, insert NULL.

    Usecase: Unique, but optional slug. Unique constrains only applies
             to the values which are not NULL.

    class MyModel(models.Model):
        slug = SlugField(null=True, unique=True, blank=True)

    If you want to be really sure, that no empty slug is in your table, you can use this
    in a schema migration (south):

    def forwards(self, orm):
        db.execute("ALTER TABLE myapp_foomodel add CONSTRAINT slug_not_empty CHECK (slug<>'')")

    If you have a empty slug in your table, you can use this in a data migration:

    def forwards(self, orm):
        db.execute("UPDATE myapp_foomodel SET slug=NULL WHERE slug='' ")
    """
    def get_prep_value(self, value):
        value = (value or "").strip()
        if not value:
            return None
        return value

    def get_internal_type(self):
        return "SlugField"
