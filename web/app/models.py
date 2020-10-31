from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserExtension(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='extension')
    cbd = models.CharField(max_length=100, verbose_name='商圈助力链接')
    help_num = models.IntegerField(default=0, verbose_name='被助力次数')
    be_helped_num = models.IntegerField(default=0, verbose_name='被助力次数')
    cbd_help_num = models.IntegerField(default=0, verbose_name='商圈助力次数')
    cbd_be_helped_num = models.IntegerField(default=0, verbose_name='商圈被助力次数')


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
    help_type = models.BooleanField()  # 0:home 1:cdb
    date_time = models.DateTimeField(auto_now_add=True)
