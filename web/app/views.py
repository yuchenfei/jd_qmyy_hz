import datetime
import re

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Q

from .models import Log

home_pattern = re.compile(
    r'https:\/\/bunearth\.m\.jd\.com\/babelDiy\/Zeus\/4SJUHwGdUQYgg94PFzjZZbGZRjDd\/index\.html\?shareType=homeTask&inviteId=(.+)'
)
cbd_pattern = re.compile(
    r'https:\/\/bunearth\.m\.jd\.com\/babelDiy\/Zeus\/4SJUHwGdUQYgg94PFzjZZbGZRjDd\/index\.html\?shareType=cbdDay&inviteId=(.+)'
)
tm_pattern = re.compile(
    r'https:\/\/h5\.m\.jd\.com\/babelDiy\/Zeus\/3DDunaJMLDamrmGwu73QbqtGtbX1\/index\.html\?babelChannel=ttt2&inviteId=(.+)'
)
star_pattern = re.compile(
    r'https:\/\/h5\.m\.jd\.com\/babelDiy\/Zeus\/4DEZi5iUgrNLD9EWknrGZhCjNv7V\/index\.html\?(.+)'
)

URL = {
    'home':
    r'https://bunearth.m.jd.com/babelDiy/Zeus/4SJUHwGdUQYgg94PFzjZZbGZRjDd/index.html?shareType=homeTask&inviteId=',
    'cbd':
    r'https://bunearth.m.jd.com/babelDiy/Zeus/4SJUHwGdUQYgg94PFzjZZbGZRjDd/index.html?shareType=cbdDay&inviteId=',
    'tm':
    r'https://h5.m.jd.com/babelDiy/Zeus/3DDunaJMLDamrmGwu73QbqtGtbX1/index.html?babelChannel=ttt2&inviteId=',
    'star':
    r'https://h5.m.jd.com/babelDiy/Zeus/4DEZi5iUgrNLD9EWknrGZhCjNv7V/index.html?'
}
LOG_TYPE = {'home': 0, 'cbd': 1, 'tm': 2, 'star': 3}


def _update_info(request, user):
    """每日首次登录更新信息"""
    today = datetime.date.today()
    if user.last_login and not user.last_login.date() == today:
        base_query = Log.objects.filter(date_time__contains=today)
        user.extension.home_help_num = base_query.filter(source=user,
                                                         help_type=0).count()
        user.extension.home_be_helped_num = base_query.filter(
            target=user, help_type=0).count()
        user.extension.cbd_help_num = base_query.filter(source=user,
                                                        help_type=1).count()
        user.extension.cbd_be_helped_num = base_query.filter(
            target=user, help_type=1).count()
        user.extension.tm_help_num = base_query.filter(source=user,
                                                       help_type=2).count()
        user.extension.tm_be_helped_num = base_query.filter(
            target=user, help_type=2).count()
        user.extension.star_help_num = base_query.filter(source=user,
                                                         help_type=3).count()
        user.extension.star_be_helped_num = base_query.filter(
            target=user, help_type=3).count()
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)


def signin(request):
    if request.POST:
        home_link = request.POST['home_link']
        cbd_link = request.POST['cbd_link']
        tm_link = request.POST['tm_link']
        star_link = request.POST['star_link']
        home_match = re.match(home_pattern, home_link.strip())
        cbd_match = re.match(cbd_pattern, cbd_link.strip())
        tm_match = re.match(tm_pattern, tm_link.strip())
        star_match = re.match(star_pattern, star_link.strip())
        if home_match:
            home_id = home_match.group(1)
            cbd_id = cbd_match.group(1) if cbd_match else ''
            tm_id = tm_match.group(1) if tm_match else ''
            star_id = star_match.group(1) if star_match else ''
            query = User.objects.filter(username=home_id)
            if not query:  # 新加入用户
                user = User.objects.create_user(username=home_id)
                user.extension.cbd = cbd_id
                user.extension.tm = tm_id
                user.extension.star = star_id
                user.save()
                # 无密码登录
            else:  # 已加入用户
                user = query[0]
                #  更新链接信息
                if cbd_id and not cbd_id == user.extension.cbd:
                    user.extension.cbd = cbd_id
                    user.save()
                if tm_id and not tm_id == user.extension.tm:
                    user.extension.tm = tm_id
                    user.save()
                if star_id and not star_id == user.extension.star:
                    user.extension.star = star_id
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
    data['help_home_url'] = URL['home'] + user.username
    data['help_cbd_url'] = URL[
        'cbd'] + user.extension.cbd if user.extension.cbd else ''
    data['help_tm_url'] = URL[
        'tm'] + user.extension.tm if user.extension.tm else ''
    data['help_star_url'] = URL[
        'star'] + user.extension.star if user.extension.star else ''
    data['num'] = [
        5 - user.extension.home_help_num,
        5 - user.extension.cbd_help_num,
        5 - user.extension.tm_help_num,
        5 - user.extension.star_help_num,  #星店长每日上限还未知，未应用
    ]
    return render(request, 'app/home.html', data)


def _help(request, type_str):
    if request.POST:
        id_list = request.POST['id_list'].split(',')
        src_user = request.user
        for id in id_list:
            user = User.objects.get(username=id)
            attr = f'{type_str}_be_helped_num'
            setattr(user.extension, attr, getattr(user.extension, attr) + 1)
            user.save()
            log = Log.objects.create(source=src_user,
                                     target=user,
                                     help_type=LOG_TYPE[type_str])
        attr = f'{type_str}_help_num'
        setattr(src_user.extension, attr,
                getattr(src_user.extension, attr) + len(id_list))
        src_user.save()
        return redirect('home')

    num = int(request.GET.get('num', 5))
    today = datetime.date.today()
    logs = Log.objects.filter(source=request.user,
                              date_time__contains=today,
                              help_type=LOG_TYPE[type_str]).all()
    already_helped_user_list = set([log.target.username for log in logs])
    # 排除 未激活（被封）、用户自己、今日已助力的
    base_query = User.objects.exclude(
        Q(is_active=False) | Q(username=request.user.username)
        | Q(username__in=already_helped_user_list))
    if not type_str == 'home':
        base_query = base_query.exclude(**{f'extension__{type_str}': ''})
    # 筛选今天登录且进行过助力
    query = base_query.filter(last_login__contains=today,
                              **{f'extension__{type_str}_help_num__gt': 0})
    if not query.count() > 0:
        query = base_query.all()

    user_list = query.order_by(f'extension__{type_str}_be_helped_num')[:num]
    data = {}
    data['user_list'] = user_list
    data['id_list'] = ','.join([user.username for user in user_list])
    if type_str == 'home':
        data['url'] = ', '.join(
            [URL[type_str] + user.username for user in user_list])
    else:
        data['url'] = ', '.join([
            URL[type_str] + getattr(user.extension, type_str)
            for user in user_list
        ])
    return render(request, f'app/help_{type_str}.html', data)


def help_home(request):
    return _help(request, 'home')


def help_cbd(request):
    return _help(request, 'cbd')


def help_tm(request):
    return _help(request, 'tm')


def help_star(request):
    return _help(request, 'star')