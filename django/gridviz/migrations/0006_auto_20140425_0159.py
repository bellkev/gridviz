# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gridviz', '0005_svgattribute_data_type'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SvgLengthDatum',
            new_name='SvgFloatDatum',
        ),
        migrations.CreateModel(
            name='SvgCharDatum',
            fields=[
                (u'svgdatumbase_ptr', models.OneToOneField(auto_created=True, primary_key=True, to_field=u'id', serialize=False, to='gridviz.SvgDatumBase')),
                ('value', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=('gridviz.svgdatumbase',),
        ),
    ]
