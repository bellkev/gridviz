# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gridviz', '0003_svgdatumbase'),
    ]

    operations = [
        migrations.CreateModel(
            name='SvgLengthDatum',
            fields=[
                (u'svgdatumbase_ptr', models.OneToOneField(auto_created=True, primary_key=True, to_field=u'id', serialize=False, to='gridviz.SvgDatumBase')),
                ('value', models.FloatField()),
            ],
            options={
            },
            bases=('gridviz.svgdatumbase',),
        ),
    ]
