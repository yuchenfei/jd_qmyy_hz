import datetime
import re

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser

from .models import Log

home_pattern = re.compile(
    r'https:\/\/bunearth\.m\.jd\.com\/babelDiy\/Zeus\/4SJUHwGdUQYgg94PFzjZZbGZRjDd\/index\.html\?shareType=homeTask&inviteId=(.+)'
)
cbd_pattern = re.compile(
    r'https:\/\/bunearth\.m\.jd\.com\/babelDiy\/Zeus\/4SJUHwGdUQYgg94PFzjZZbGZRjDd\/index\.html\?shareType=cbdDay&inviteId=(.+)'
)
home_url = r'https://bunearth.m.jd.com/babelDiy/Zeus/4SJUHwGdUQYgg94PFzjZZbGZRjDd/index.html?shareType=homeTask&inviteId='
cbd_url = r'https://bunearth.m.jd.com/babelDiy/Zeus/4SJUHwGdUQYgg94PFzjZZbGZRjDd/index.html?shareType=cbdDay&inviteId='


def _update_info(request, user):
    """每日首次登录更新信息"""
    today = datetime.date.today()
    if user.last_login and not user.last_login.date() == today:
        base_query = Log.objects.filter(date_time__contains=today)
        user.extension.help_num = base_query.filter(source=user,
                                                    help_type=0).count()
        user.extension.be_helped_num = base_query.filter(target=user,
                                                         help_type=0).count()
        user.extension.cbd_help_num = base_query.filter(source=user,
                                                        help_type=1).count()
        user.extension.cbd_be_helped_num = base_query.filter(
            target=user, help_type=1).count()
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)


def signin(request):
    if request.POST:
        home_link = request.POST['home_link']
        cbd_link = request.POST['cbd_link']
        home_match = re.match(home_pattern, home_link.strip())
        cbd_match = re.match(cbd_pattern, cbd_link.strip())
        if home_match and cbd_match:
            home_id = home_match.group(1)
            cbd_id = cbd_match.group(1)
            query = User.objects.filter(username=home_id)
            if not query:  # 新加入用户
                user = User.objects.create_user(username=home_id)
                user.extension.cbd = cbd_id
                user.save()
                # 无密码登录
            else:  # 已加入用户
                user = query[0]
                if not cbd_id == user.extension.cbd:
                    user.extension.cbd = cbd_id
                    user.save()
                _update_info(request, user)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, '助力链接或商圈链接格式不正确，请检查后重试')
    return render(request, 'app/signin.html')


def signout(request):
    logout(request)
    return redirect('signin')


def home(request):
    user = request.user
    if user.is_anonymous:
        return redirect('signin')
    _update_info(request, user)
    data = {}
    data['help_home_url'] = home_url + user.username
    data['help_cbd_url'] = cbd_url + user.extension.cbd
    return render(request, 'app/home.html', data)


def help_home(request):
    if request.POST:
        id_list = request.POST['id_list'].split(',')
        src_user = request.user
        for id in id_list:
            user = User.objects.get(username=id)
            user.extension.be_helped_num += 1
            user.save()
            log = Log.objects.create(source=src_user, target=user, help_type=0)
        src_user.extension.help_num += len(id_list)
        src_user.save()
        return redirect('home')
    # 筛选今天登录且进行过助力
    base_query = User.objects.exclude(username=request.user.username)
    today = datetime.date.today()
    query = base_query.filter(last_login__contains=today,
                              extension__help_num__gt=0)
    if query.count() < 5:
        query = base_query.all()

    user_list = query.order_by('extension__be_helped_num')[:5]
    data = {}
    data['user_list'] = user_list
    data['id_list'] = ','.join([user.username for user in user_list])
    data['url'] = ', '.join([home_url + user.username for user in user_list])
    return render(request, 'app/help_home.html', data)


def help_cbd(request):
    if request.POST:
        id_list = request.POST['id_list'].split(',')
        src_user = request.user
        for id in id_list:
            user = User.objects.get(username=id)
            user.extension.cbd_be_helped_num += 1
            user.save()
            log = Log.objects.create(source=src_user, target=user, help_type=1)
        src_user.extension.cbd_help_num += len(id_list)
        src_user.save()
        return redirect('home')
    # 筛选今天登录且进行过商圈助力
    base_query = User.objects.exclude(username=request.user.username)
    today = datetime.date.today()
    query = base_query.filter(last_login__contains=today,
                              extension__cbd_help_num__gt=0)
    if query.count() < 5:
        query = base_query.all()

    user_list = query.order_by('extension__cbd_be_helped_num')[:5]
    data = {}
    data['user_list'] = user_list
    data['id_list'] = ','.join([user.username for user in user_list])
    data['url'] = ', '.join(
        [cbd_url + user.extension.cbd for user in user_list])
    return render(request, 'app/help_cbd.html', data)