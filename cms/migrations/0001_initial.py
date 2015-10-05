# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('home', models.BooleanField(default=False)),
                ('published', models.BooleanField(verbose_name='Active', default=False)),
                ('approval_needed', models.BooleanField(default=False)),
                ('template', models.CharField(max_length=250, default='cms/page.html')),
                ('display_title', models.CharField(verbose_name='Display title', max_length=250)),
                ('slug', models.SlugField(verbose_name='Unique Page Identifier', blank=True, max_length=60, null=True)),
                ('order_id', models.IntegerField(default=0)),
                ('publish', models.BooleanField(verbose_name='Publish this page. The page will also be set to Active.', default=False)),
                ('approve', models.BooleanField(verbose_name='Submit for approval', default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('redirect_to_url', models.URLField(verbose_name='Redirect to URL', blank=True, help_text='Redirect this page to a given URL')),
                ('target', models.CharField(verbose_name='Open page in', choices=[('_self', 'the same window'), ('_blank', 'a new window')], max_length=50, default='_self')),
                ('hide_from_nav', models.BooleanField(verbose_name='Hide from navigation', default=False)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
                'permissions': (('can_publish', 'Can publish'),),
            },
        ),
        migrations.CreateModel(
            name='PageDataSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('config', models.TextField()),
            ],
            options={
                'verbose_name': 'Page data set',
                'verbose_name_plural': 'Page data sets',
            },
        ),
        migrations.CreateModel(
            name='PageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(verbose_name='Page title', max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('language_code', models.CharField(verbose_name='language', choices=[('af', 'Afrikaans'), ('ar', 'Arabic'), ('ast', 'Asturian'), ('az', 'Azerbaijani'), ('bg', 'Bulgarian'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('br', 'Breton'), ('bs', 'Bosnian'), ('ca', 'Catalan'), ('cs', 'Czech'), ('cy', 'Welsh'), ('da', 'Danish'), ('de', 'German'), ('el', 'Greek'), ('en', 'English'), ('en-au', 'Australian English'), ('en-gb', 'British English'), ('eo', 'Esperanto'), ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'), ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'), ('eu', 'Basque'), ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('ga', 'Irish'), ('gl', 'Galician'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hr', 'Croatian'), ('hu', 'Hungarian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('ja', 'Japanese'), ('ka', 'Georgian'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'), ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'), ('mr', 'Marathi'), ('my', 'Burmese'), ('nb', 'Norwegian Bokmal'), ('ne', 'Nepali'), ('nl', 'Dutch'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('tt', 'Tatar'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('vi', 'Vietnamese'), ('zh-cn', 'Simplified Chinese'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese'), ('zh-tw', 'Traditional Chinese')], max_length=7)),
                ('content', models.TextField(blank=True)),
                ('live_content', models.TextField(blank=True)),
                ('parent', models.ForeignKey(related_name='translations', to='cms.Page')),
            ],
            options={
                'verbose_name': 'Translation',
                'abstract': False,
                'verbose_name_plural': 'Translations',
            },
            bases=(models.Model, cms.models.PublishTranslation),
        ),
        migrations.AddField(
            model_name='page',
            name='dataset',
            field=models.ForeignKey(blank=True, null=True, to='cms.PageDataSet'),
        ),
        migrations.AddField(
            model_name='page',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, related_name='children', to='cms.Page'),
        ),
        migrations.AddField(
            model_name='page',
            name='published_from',
            field=models.ForeignKey(blank=True, null=True, to='cms.Page'),
        ),
        migrations.AddField(
            model_name='page',
            name='redirect_to',
            field=models.ForeignKey(blank=True, null=True, related_name='redirect_to_page', to='cms.Page'),
        ),
        migrations.AddField(
            model_name='page',
            name='related_pages',
            field=models.ManyToManyField(related_name='related_pages_rel_+', blank=True, to='cms.Page'),
        ),
        migrations.AlterUniqueTogether(
            name='pagetranslation',
            unique_together=set([('parent', 'language_code')]),
        ),
    ]
