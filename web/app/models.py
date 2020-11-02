from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserExtension(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='extension')
    help_num = models.IntegerField(default=0, verbose_name='被助力次数')
    be_helped_num = models.IntegerField(default=0, verbose_name='被助力次数')
    cbd = models.CharField(max_length=100, default='', verbose_name='商圈助力链接')
    cbd_help_num = models.IntegerField(default=0, verbose_name='商圈助力次数')
    cbd_be_helped_num = models.IntegerField(default=0, verbose_name='商圈被助力次数')
    tm = models.CharField(max_length=100, default='', verbose_name='时光机助力链接')
    tm_help_num = models.IntegerField(default=0, verbose_name='时光机助力次数')
    tm_be_helped_num = models.IntegerField(default=0, verbose_name='时光机被助力次数')
    star = models.CharField(max_length=200, default='', verbose_name='星店长助力链接')
    star_help_num = models.IntegerField(default=0, verbose_name='星店长助力次数')
    star_be_helped_num = models.IntegerField(default=0,
                                             verbose_name='星店长被助力次数')


@receiver(post_save, sender=User)
def create_user_extension(sender, instance, created, **kwargs):
    if created:
        UserExtension.objects.create(user=instance)
    instance.extension.save()


class Log(models.Model):
    source = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='help')
    target = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='be_help')
    help_type = models.IntegerField()  # 0:home 1:cdb
    date_time = models.DateTimeField(auto_now_add=True)
