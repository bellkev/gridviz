# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gridviz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SvgAttribute',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SvgElementType',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SvgElement',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.ForeignKey(to='gridviz.SvgElementType', to_field=u'id')),
                ('drawing', models.ForeignKey(to='gridviz.Drawing', to_field=u'id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
