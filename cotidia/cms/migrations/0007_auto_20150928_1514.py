# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0006_image_width'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='size',
        ),
        migrations.AddField(
            model_name='image',
            name='display_width',
            field=models.IntegerField(blank=True, null=True, max_length=100),
        ),
        migrations.AddField(
            model_name='image',
            name='height',
            field=models.IntegerField(blank=True, null=True, max_length=100),
        ),
    ]
