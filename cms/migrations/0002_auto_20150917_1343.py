# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'verbose_name_plural': 'Pages', 'verbose_name': 'Page', 'permissions': (('publish_page', 'Can publish page'),)},
        ),
        migrations.AddField(
            model_name='page',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='created_by'),
        ),
        migrations.AddField(
            model_name='page',
            name='updated_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='updated_by'),
        ),
    ]
