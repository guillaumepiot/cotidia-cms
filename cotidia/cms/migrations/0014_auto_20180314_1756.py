# Generated by Django 2.0.1 on 2018-03-14 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_auto_20180109_1656'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagetranslation',
            options={'verbose_name': 'Translation', 'verbose_name_plural': 'Translations'},
        ),
        migrations.AlterField(
            model_name='pagetranslation',
            name='language_code',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French')], max_length=7, verbose_name='language'),
        ),
    ]
