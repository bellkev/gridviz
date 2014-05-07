# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        (b'sql_svg_store', b'0002_svgdatumbase'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'SvgCharDatum',
            fields=[
                ('svgdatumbase_ptr', models.OneToOneField(auto_created=True, primary_key=True, to_field='id', serialize=False, to=b'sql_svg_store.SvgDatumBase')),
                (b'value', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(b'sql_svg_store.svgdatumbase',),
        ),
    ]
