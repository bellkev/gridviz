# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        (b'drawings', b'__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'SvgAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name', models.CharField(max_length=20)),
                (b'data_type', models.PositiveSmallIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'SvgElementType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'SvgElement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'type', models.ForeignKey(to=b'sql_svg_store.SvgElementType', to_field='id')),
                (b'drawing', models.ForeignKey(to=b'drawings.Drawing', to_field='id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
