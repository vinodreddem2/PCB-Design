# Generated by Django 5.0.10 on 2025-02-14 13:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('right_to_draw', '0007_caddesigntemplates_secondary_sub_level'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadapprovertemplates',
            name='created_by',
            field=models.ForeignKey(blank=True, db_column='CREATED_BY', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cadapprovertemplates',
            name='updated_by',
            field=models.ForeignKey(blank=True, db_column='UPDATED_BY', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='caddesigntemplates',
            name='created_by',
            field=models.ForeignKey(blank=True, db_column='CREATED_BY', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='caddesigntemplates',
            name='updated_by',
            field=models.ForeignKey(blank=True, db_column='UPDATED_BY', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cadverifiertemplates',
            name='created_by',
            field=models.ForeignKey(blank=True, db_column='CREATED_BY', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cadverifiertemplates',
            name='updated_by',
            field=models.ForeignKey(blank=True, db_column='UPDATED_BY', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
