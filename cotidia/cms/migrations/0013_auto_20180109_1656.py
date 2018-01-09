# Generated by Django 2.0.1 on 2018-01-09 16:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20180109_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='page',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='cms.Page'),
        ),
        migrations.AlterField(
            model_name='page',
            name='redirect_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='redirect_to_page', to='cms.Page'),
        ),
        migrations.AlterField(
            model_name='page',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pagetranslation',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='translation_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pagetranslation',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='cms.Page'),
        ),
        migrations.AlterField(
            model_name='pagetranslation',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='translation_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
