# Generated by Django 3.1.2 on 2020-11-02 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20201102_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextension',
            name='star',
            field=models.CharField(default='', max_length=200, verbose_name='星店长助力链接'),
        ),
        migrations.AddField(
            model_name='userextension',
            name='star_be_helped_num',
            field=models.IntegerField(default=0, verbose_name='星店长被助力次数'),
        ),
        migrations.AddField(
            model_name='userextension',
            name='star_help_num',
            field=models.IntegerField(default=0, verbose_name='星店长助力次数'),
        ),
        migrations.AddField(
            model_name='userextension',
            name='tm',
            field=models.CharField(default='', max_length=100, verbose_name='时光机助力链接'),
        ),
        migrations.AddField(
            model_name='userextension',
            name='tm_be_helped_num',
            field=models.IntegerField(default=0, verbose_name='时光机被助力次数'),
        ),
        migrations.AddField(
            model_name='userextension',
            name='tm_help_num',
            field=models.IntegerField(default=0, verbose_name='时光机助力次数'),
        ),
    ]
