from django.http import HttpResponse
from west.models import Character
from django.shortcuts import render
from django.template.context_processors import csrf
from django.shortcuts import render, redirect
from django.contrib.auth import *
from django.contrib.auth.forms import UserCreationForm


def staff(request):
    context = {}
    context['label'] = 'Hello World!'
    return render(request, 'templay.html', context)


def first_page(request):
    return HttpResponse("<p>西餐</p>")


def templay(request):
    staff_list = Character.objects.all()
    return render(request, 'templay.html', {'staffs': staff_list})


def form(request):
    return render(request, 'form.html')


# def investigate(request):
#     rlt = request.GET['staff']
#     return HttpResponse(rlt)


def investigate(request):
    if request.POST:
        submitted = request.POST['staff']
        new_record = Character(name=submitted)
        new_record.save()
    ctx = {}
    ctx.update(csrf(request))
    all_records = Character.objects.all()
    ctx['staff'] = all_records
    return render(request, "investigate.html", ctx)


def user_login(request):
    if request.POST:
        username = password = ''
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('/west/main')
    ctx = {}
    ctx.update(csrf(request))
    return render(request, 'login.html', ctx)


def user_logout(request):
    '''
    logout
    URL: /users/logout
    '''
    logout(request)
    return redirect('west/users/login')


def diff_response(request):
    if request.user.is_authenticated():
        content = "<p>my dear user</p>"
    else:
        content = "<p>you wired stranger</p>"
    return HttpResponse(content)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print('user created!')
            new_user = form.save()
        else:
            print('form is invalid!')
            return redirect("/west/users/register")
        return redirect("/")
    else:
        form = UserCreationForm()
        ctx = {'form': form}
        ctx.update(csrf(request))
        return render(request, "register.html", ctx)


def main(request):
    return render(request, 'main.html')


def Bdanmaku2pic(request):
    if request.method == 'POST':
        avid = request.POST.get('avid')

        try:
            import requests
            from bs4 import BeautifulSoup
            import re
            from wordcloud import WordCloud

            html = requests.get('http://www.bilibili.com/video/av' + avid + '/')  # 此处url填写需要访问的地址
            soup = BeautifulSoup(html.content, 'lxml')

            sc = soup.find('script', text=re.compile("EmbedPlayer*"))  # 找到有特定词的script,re是regular expression正则表达是
            # print(str(sc))
            sc1 = str(sc)
            a = sc1.find('cid=');
            b = sc1.find('&');
            sc2 = sc1[a + 4:b]
            print(sc2)
            file = requests.get("http://comment.bilibili.com/" + sc2 + ".xml")
            soupxml = BeautifulSoup(file.content, 'lxml')
            # print(soupxml.prettify())
            ds = soupxml.find_all('d')

            cuttext = ''
            for d in ds:
                cuttext = cuttext + ' ' + str(d.text);
            print(cuttext)
            # 初始化词云
            cloud = WordCloud(
                # 设置字体，不指定就会出现乱码
                font_path="templates/static/ttc/SourceHanSerif-Heavy.ttc",
                # 设置背景色
                background_color='white',
                # 词云形状
                # mask=color_mask,
                # 允许最大词汇
                max_words=100,
                # # 最大号字体
                # max_font_size=40
            )
            word_cloud = cloud.generate_from_text(cuttext)  # 产生词云
            word_cloud.to_file('templates/static/image/biliPic/' + avid + ".png")  # 保存图片
            file_path = '/static/image/biliPic/'+avid+'.png'
            return render(request, 'Bdanmaku2pic.html', {'file_path': file_path})
        except:
            file_path ='抱歉，转换失败'
            return render(request, 'Bdanmaku2pic.html')


    else:
        return render(request, 'Bdanmaku2pic.html')
