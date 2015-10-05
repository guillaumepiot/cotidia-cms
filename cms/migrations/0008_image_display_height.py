# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0007_auto_20150928_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='display_height',
            field=models.IntegerField(null=True, blank=True, max_length=100),
        ),
    ]
