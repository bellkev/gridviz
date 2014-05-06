# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        (b'gridviz', b'0006_auto_20140425_0159'),
    ]

    operations = [
        migrations.AddField(
            model_name=b'drawing',
            name=b'created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=1, to_field='id'),
            preserve_default=False,
        ),
    ]
