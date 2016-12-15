# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0008_image_display_height'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='display_height',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='display_width',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='height',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='width',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='pagetranslation',
            name='language_code',
            field=models.CharField(max_length=7, verbose_name='language', choices=[(b'en', b'English'), (b'fr', b'French')]),
        ),
    ]
