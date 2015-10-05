# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0004_pagetranslation_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='size',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
    ]
