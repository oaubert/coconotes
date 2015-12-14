# -*- coding: utf-8 -*-
from django.db import migrations

def create_licenses(apps, schema_editor):
    License = apps.get_model("coco", "License")
    for l in (
            ('cc-by',
             'Attribution',
             'http://creativecommons.org/licenses/by/4.0',
             'https://licensebuttons.net/l/by/3.0/88x31.png'),
            ('cc-by-sa',
             'Attribution-ShareAlike',
             'http://creativecommons.org/licenses/by-sa/4.0',
             'https://licensebuttons.net/l/by-sa/3.0/88x31.png'),
            ('cc-by-nd',
             'Attribution-NoDerivs',
             'http://creativecommons.org/licenses/by-nd/4.0',
             'https://licensebuttons.net/l/by-nd/3.0/88x31.png'),
            ('cc-by-nc',
             'Attribution-NonCommercial',
             'http://creativecommons.org/licenses/by-nc/4.0',
             'https://licensebuttons.net/l/by-nc/3.0/88x31.png'),
            ('cc-by-nc-sa',
             'Attribution-NonCommercial-ShareAlike',
             'http://creativecommons.org/licenses/by-nc-sa/4.0',
             'https://licensebuttons.net/l/by-nc/3.0/88x31.png'),
            ('cc-by-nc-nd',
             'Attribution-NonCommercial-NoDerivs',
             'http://creativecommons.org/licenses/by-nc-nd/4.0',
             'https://licensebuttons.net/l/by-nc-nd/3.0/88x31.png'),
            ):
        License.objects.create(slug=l[0],
                               title=l[1],
                               url=l[2],
                               thumbnail=l[3])

class Migration(migrations.Migration):

    dependencies = [
        ('coco', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_licenses),
    ]
