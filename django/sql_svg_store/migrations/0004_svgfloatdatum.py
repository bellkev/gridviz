# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        (b'sql_svg_store', b'0003_svgchardatum'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'SvgFloatDatum',
            fields=[
                ('svgdatumbase_ptr', models.OneToOneField(auto_created=True, primary_key=True, to_field='id', serialize=False, to=b'sql_svg_store.SvgDatumBase')),
                (b'value', models.FloatField()),
            ],
            options={
            },
            bases=(b'sql_svg_store.svgdatumbase',),
        ),
    ]
