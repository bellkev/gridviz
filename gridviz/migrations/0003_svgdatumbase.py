# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gridviz', '0002_svgattribute_svgelement_svgelementtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='SvgDatumBase',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('element', models.ForeignKey(to='gridviz.SvgElement', to_field=u'id')),
                ('attribute', models.ForeignKey(to='gridviz.SvgAttribute', to_field=u'id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
