# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gridviz', '0004_svglengthdatum'),
    ]

    operations = [
        migrations.AddField(
            model_name='svgattribute',
            name='data_type',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
