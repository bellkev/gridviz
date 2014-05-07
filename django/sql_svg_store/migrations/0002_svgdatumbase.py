# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        (b'sql_svg_store', b'0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'SvgDatumBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'element', models.ForeignKey(to=b'sql_svg_store.SvgElement', to_field='id')),
                (b'attribute', models.ForeignKey(to=b'sql_svg_store.SvgAttribute', to_field='id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
