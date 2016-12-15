# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0002_auto_20150917_1343'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images', null=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-created',),
                'verbose_name_plural': 'Images',
                'verbose_name': 'Image',
            },
        ),
        migrations.RenameField(
            model_name='pagetranslation',
            old_name='live_content',
            new_name='regions',
        ),
        migrations.AddField(
            model_name='pagetranslation',
            name='created_by',
            field=models.ForeignKey(related_name='translation_created_by', to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pagetranslation',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pagetranslation',
            name='date_updated',
            field=models.DateTimeField(auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pagetranslation',
            name='updated_by',
            field=models.ForeignKey(related_name='translation_updated_by', to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pagetranslation',
            name='language_code',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French'), ('de', 'Deutsche')], max_length=7, verbose_name='language'),
        ),
    ]
