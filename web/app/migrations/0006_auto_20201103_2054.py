# Generated by Django 3.1.2 on 2020-11-03 20:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20201103_1521'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userextension',
            old_name='be_helped_num',
            new_name='home_be_helped_num',
        ),
        migrations.RenameField(
            model_name='userextension',
            old_name='help_num',
            new_name='home_help_num',
        ),
    ]