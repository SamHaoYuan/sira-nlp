# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-23 04:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_add_comment_metrics'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['created'], name='review_created_idx'),
        ),
    ]
