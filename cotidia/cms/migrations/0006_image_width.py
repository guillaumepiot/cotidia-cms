# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_image_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='width',
            field=models.IntegerField(max_length=100, null=True, blank=True),
        ),
    ]
