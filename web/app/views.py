import datetime
import re

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render

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
PATTERN = {
    'home': {
        'report':
        re.compile(r'(\d\d:\d\d:\d\d) \[帮TA助力\](....)！(.+)\((\d)\/\d\)')
    },
    'cbd': {
        'report':
        re.compile(r'(\d\d:\d\d:\d\d) \[帮助商圈助力\](....)！(.+)\((\d)\/\d\)')
    },
    'tm': {
        'report':
        re.compile(r'(\d\d:\d\d:\d\d) \[时光机助力\](....)！(.*)\((\d+)\/\d\)')
    },
    'star': {
        'report':
        re.compile(r'(\d\d:\d\d:\d\d) \[星店长助力\](....)！(.*)\((\d+)\/\d\)')
    }
}

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


def _update_info(user, request=None):
    """更新信息，并按需刷新登录时间"""
    today = datetime.date.today()
    base_query = Log.objects.filter(date_time__contains=today)
    user.extension.home_help_num = \
        base_query.filter(source=user, help_type=0).count()
    user.extension.home_be_helped_num = \
        base_query.filter(target=user, help_type=0).count()
    user.extension.cbd_help_num = \
        base_query.filter(source=user, help_type=1).count()
    user.extension.cbd_be_helped_num = \
        base_query.filter(target=user, help_type=1).count()
    user.extension.tm_help_num = \
        base_query.filter(source=user, help_type=2).count()
    user.extension.tm_be_helped_num = \
        base_query.filter(target=user, help_type=2).count()
    user.extension.star_help_num = \
        base_query.filter(source=user, help_type=3).count()
    user.extension.star_be_helped_num = \
        base_query.filter(target=user, help_type=3).count()
    user.save()
    if request:
        if user.last_login and not user.last_login.date() == today:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)


def signin(request):
    """录入信息"""
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
                _update_info(user)  # 仅刷新首页数据
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, '助力链接格式不正确，请检查后重试')
    return render(request, 'app/signin.html')


def signout(request):
    """退出"""
    logout(request)
    return redirect('signin')


def home(request):
    """首页视图"""
    user = request.user
    if user.is_anonymous:
        return redirect('signin')
    _update_info(user, request)  # 更新数据，并刷新登录时间
    data = {}
    data['help_home_url'] = URL['home'] + user.username
    data['help_cbd_url'] = URL['cbd'] + \
        user.extension.cbd if user.extension.cbd else ''
    data['help_tm_url'] = URL['tm'] + \
        user.extension.tm if user.extension.tm else ''
    data['help_star_url'] = URL['star'] + \
        user.extension.star if user.extension.star else ''
    data['num'] = [
        5 - user.extension.home_help_num,
        5 - user.extension.cbd_help_num,
        5 - user.extension.tm_help_num,
        5 - user.extension.star_help_num,
    ]
    return render(request, 'app/home.html', data)


def help_home(request):
    """个人助力"""
    return _help(request, 'home')


def help_cbd(request):
    """商圈助力"""
    return _help(request, 'cbd')


def help_tm(request):
    """时光机助力"""
    return _help(request, 'tm')


def help_star(request):
    """星店长助力"""
    return _help(request, 'star')


def _help(request, type_str):
    """助力处理入口"""
    if request.POST:
        return _handle_help_post_request(request, type_str)
    return _handle_help_get_request(request, type_str)


def _handle_help_get_request(request, type_str):
    """处理助力页面 GET 请求"""
    num = int(request.GET.get('num', 5))
    # check num
    num = 0 if num < 0 else num
    num = 5 if num > 5 else num
    today = datetime.date.today()
    if type_str == 'tm':  # 时光机助力只能帮助一次，不用分是否是今日的
        logs = Log.objects.filter(Q(help_type=LOG_TYPE[type_str])
                                  | Q(help_type=LOG_TYPE[type_str] + 4),
                                  source=request.user).all()
    else:
        logs = Log.objects.filter(Q(help_type=LOG_TYPE[type_str])
                                  | Q(help_type=LOG_TYPE[type_str] + 4),
                                  source=request.user,
                                  date_time__contains=today).all()
    already_helped_user_list = set([log.target.username for log in logs])
    # 排除 未激活（被封）、用户自己、今日已助力过 & 忽略的
    base_query = User.objects.exclude(
        Q(is_active=False) | Q(username=request.user.username)
        | Q(username__in=already_helped_user_list))
    if not type_str == 'home':
        base_query = base_query.exclude(**{f'extension__{type_str}': ''})
    # 筛选今天登录且进行过助力
    query = base_query.filter(last_login__contains=today,
                              **{f'extension__{type_str}_help_num__gt': 0})
    update = False
    if not query.count() > 0:
        update = True
        query = base_query.all()

    user_list = query.order_by(f'extension__{type_str}_be_helped_num')[:num]
    if update:
        [
            _update_info(user) for user in user_list
            if getattr(user.extension, f'{type_str}_help_num') +
            getattr(user.extension, f'{type_str}_be_helped_num') > 0
        ]
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


def _handle_help_post_request(request, type_str):
    """处理助力页面 POST 请求"""
    src_user = request.user
    id_list = request.POST['id_list'].split(',')
    report = request.POST.get('report', '')
    data = [{'id': id_} for id_ in id_list]  # 用于组合链接和对应反馈
    report_list = report.strip().split('\n')
    if not len(data) == len(report_list):
        return JsonResponse({'status': 'error', 'message': '反馈结束数量与链接数不一致'})
    # 解析反馈信息
    for i, line in enumerate(report.strip().split('\n')):
        match = re.match(PATTERN[type_str]['report'], line.strip())
        if match:
            time = match.group(1)
            result = match.group(2)
            info = match.group(3)
            if type_str == 'tm':  # 时光机索引会出现 (23206264/1)
                index = len(data) - 1 - i
            else:
                index = int(match.group(4)) - 1
            print(index, range(len(data)))
            if index not in range(len(data)):
                return JsonResponse({
                    'status': 'error',
                    'message': '执行结果索引与链接数量不匹配，请检查结果是否复制正确'
                })
            data[index].update({'time': time, 'result': result, 'info': info})
        else:
            return JsonResponse({
                'status': 'error',
                'message': '执行结果解析异常，请检查结果是否复制正确'
            })
    # 根据反馈情况处理链接
    print(data)
    success = 0
    for item in data:
        user = User.objects.get(username=item['id'])
        if item['result'] == '助力成功':
            success += 1
            attr = f'{type_str}_be_helped_num'
            setattr(user.extension, attr, getattr(user.extension, attr) + 1)
            user.save()
            Log.objects.create(source=src_user,
                               target=user,
                               help_type=LOG_TYPE[type_str])
        elif item['result'] == '操作成功':
            if item['info'] == '' and type_str == 'star':
                success += 1
                attr = f'{type_str}_be_helped_num'
                setattr(user.extension, attr,
                        getattr(user.extension, attr) + 1)
                user.save()
                Log.objects.create(source=src_user,
                                   target=user,
                                   help_type=LOG_TYPE[type_str])
            if item['info'].startswith('谢谢你！本场挑战已结束'):
                return JsonResponse({'status': 'error', 'message': '本场挑战已结束'})
            elif item['info'].startswith('您今天已经帮') \
                or item['info'].startswith('好友人气爆棚') \
                    or item['info'].startswith('已为此人助力过'):
                # 今日忽略该 ID
                Log.objects.create(source=src_user,
                                   target=user,
                                   help_type=(LOG_TYPE[type_str] + 4))
            elif item['info'].startswith('挑战已结束') \
                    or item['info'].startswith('请求失败，请求参数错误'):
                # 商圈链接过时 星店长链接失效
                setattr(user.extension, type_str, '')
                user.save()
    src_user.extension.home_help_num += success
    src_user.save()
    return JsonResponse({'status': 'success', 'message': f'助力成功 {success} 次'})
