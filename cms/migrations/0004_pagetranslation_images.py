# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20150925_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagetranslation',
            name='images',
            field=models.TextField(blank=True),
        ),
    ]
