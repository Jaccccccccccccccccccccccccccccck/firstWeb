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
                if(len(str(d.text))<=10):
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


def pdf2String(request):
    if request.method == 'POST':
        print("pdf2String start!")
        myFile = request.FILES.get("pdf2trans", None)  # 获取上传的文件，如果没有文件，则默认为None
        print(myFile)
        transfered_str = '文件转换失败'
        if not myFile:
            return render(request, 'pdf2String.html', {'transfered_str': transfered_str})
        try:
            transfered_str = '';
            from pdfminer.pdfparser import PDFParser, PDFDocument
            from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
            from pdfminer.converter import PDFPageAggregator
            from pdfminer.layout import LTTextBoxHorizontal, LAParams
            from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
            praser = PDFParser(myFile)
            # 创建一个PDF文档
            doc = PDFDocument()
            # 连接分析器 与文档对象
            praser.set_document(doc)
            doc.set_parser(praser)
            # 提供初始化密码
            # 如果没有密码 就创建一个空的字符串
            doc.initialize()
            # 检测文档是否提供txt转换，不提供就忽略
            if not doc.is_extractable:
                raise PDFTextExtractionNotAllowed
            else:
                # 创建PDf 资源管理器 来管理共享资源
                rsrcmgr = PDFResourceManager()
                # 创建一个PDF设备对象
                laparams = LAParams()
                device = PDFPageAggregator(rsrcmgr, laparams=laparams)
                # 创建一个PDF解释器对象
                interpreter = PDFPageInterpreter(rsrcmgr, device)

                # 循环遍历列表，每次处理一个page的内容
                for page in doc.get_pages():  # doc.get_pages() 获取page列表
                    interpreter.process_page(page)
                    # 接受该页面的LTPage对象
                    layout = device.get_result()
                    # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
                    for x in layout:
                        if (isinstance(x, LTTextBoxHorizontal)):
                            results = x.get_text()
                            # print(results)
                            transfered_str = transfered_str + results;

            #得到文字后进一步的处理
            # re.sub(r'\r\n\s','许相虎',transfered_str)
            print("before change: \n" + transfered_str)
            transfered_str = re.sub(r'\n\s', '许相虎', transfered_str)
            transfered_str = re.sub(r'\s\n', '许相虎', transfered_str)
            print("after change: \n" + transfered_str)
            transfered_str = re.sub(r'\n|\r', '', transfered_str)
            transfered_str = re.sub(r'许相虎', '\n', transfered_str)
            transfered_str = re.sub(r'\s{4,}', '\n', transfered_str)
            print("finally: \n" + transfered_str)

            return render(request, 'pdf2String.html', {'transfered_str': transfered_str})
        except:
            return render(request, 'pdf2String.html', {'transfered_str': transfered_str})
    else:
        return render(request, 'pdf2String.html')

def ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        print("here")
        my_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        print("there")
        my_ip = request.META['REMOTE_ADDR']
    my_ip = str(my_ip).split(',')
    my_location = []
    try:
        import requests
        from bs4 import BeautifulSoup
        from lxml import etree
        for ips in my_ip:
            url = "http://www.ip.cn/index.php?ip="+ips.strip()
            print(url)
            re = requests.get(url)
            html = etree.HTML(re.text)
            node = html.xpath('//*[@id="result"]/div/p[2]/code');
            for nodes in node:
                my_location.append(nodes.text);
        print(my_location)
        return render(request, 'ip.html', {"my_ip": my_ip,"my_location":my_location})
    except:
        return render(request, 'ip.html', {"my_ip": my_ip})
    return render(request, 'ip.html',{"my_ip":my_ip})


def porn(request):
    try:
        porn_list =[]
        import requests
        from lxml import etree
        from time import time

        url = "http://www.pornfreex.us"
        print(url)
        re = requests.get(url)
        html = etree.HTML(re.text)

        # location_soup = BeautifulSoup(re.text,'html')
        # print(location_soup.prettify())
        tops = html.xpath('//*[@id="content"]/div[1]/div[2]/div/ul[3]/li');

        for top in tops:
            relate_url = top.xpath('a[1]/@href')

            # video_url = url+relate_url[0]
            # driver = webdriver.PhantomJS()
            # driver.get(video_url)  # 此处url填写需要访问的地址
            # file_url = driver.find_element_by_xpath('//*[@id="html5"]').get_attribute('src')

            title = top.xpath('a[2]/@title')
            img_url = top.xpath('a[1]/img/@src')
            times = top.xpath('a[1]/span[2]/text()')
            relate_url = top.xpath('a[1]/@href')
            video_url = url + relate_url[0]
            # print(file_url)
            porn_dict = {"title":title[0],"img_url":img_url[0],"times":times[0],"video_url":video_url}
            porn_list.append(porn_dict)

        return render(request, 'porn.html', {"porn_list": porn_list})
    except Exception:
        print(Exception)
        return render(request, 'porn.html', {"porn_list": porn_list})


def get_file_url(request):
    bef_url = request.GET.get('bef_url')
    try:
        import requests
        from lxml import etree
        from time import time
        from selenium import webdriver

        driver = webdriver.PhantomJS()
        driver.get(bef_url)  # 此处url填写需要访问的地址
        file_url = driver.find_element_by_xpath('//*[@id="html5"]').get_attribute('src')

        return HttpResponse(file_url)
    except Exception:
        return HttpResponse(status=404)

def request_info(request):
    if request.method == 'GET':
    # from django.core.handlers.wsgi import WSGIRequest
    # print(type(request))
    # print(request.environ)
        request_detail = request.META
        print(type(request_detail))
        print(request_detail)
        return render(request,'request_info.html',{'request_detail':request_detail})
    else :
        request_post_uid = request.POST.get('uid')
        return request_post_uid['uid']

def one(request):
    try:
        import requests
        from lxml import etree
        import re

        url = "http://www.wufazhuce.com/"
        res = requests.get(url)
        html = etree.HTML(res.text)
        # //*[@id="carousel-one"]/div/div[1]/a/img
        # //*[@id="carousel-one"]/div/div[1]/div[2]/div[2]/a
        # //*[@id="main-container"]/div[1]/div[2]/div/div/div[1]/div/p[2]/a
        # //*[@id="main-container"]/div[1]/div[2]/div/div/div[2]/div/p[2]/a
        # one图片
        pic = html.xpath('//*[@id="carousel-one"]/div/div[1]/a/img/@src')

        # one句子
        notes = html.xpath('//*[@id="carousel-one"]/div/div[1]/div[2]/div[2]/a/text()')
        for note in notes:
            note = re.sub(r'\r\n','',note)
        # one文章
        article_url = html.xpath('//*[@id="main-container"]/div[1]/div[2]/div/div/div[1]/div/p[2]/a/@href')
        article_author = html.xpath('//*[@id="main-container"]/div[1]/div[2]/div/div/div[1]/div/p[2]/a/small/text()')
        article_title = html.xpath('//*[@id="main-container"]/div[1]/div[2]/div/div/div[1]/div/p[2]/a/text()')

        # one问题
        question_url = html.xpath('//*[@id="main-container"]/div[1]/div[2]/div/div/div[2]/div/p[2]/a/@href')
        question_title = html.xpath('//*[@id="main-container"]/div[1]/div[2]/div/div/div[2]/div/p[2]/a/text()')

        # print(pic[0])
        # print(oneSentence)
        # print(article_title[0].strip())
        # print(article_author[0])
        # print(article_url[0])
        # print(question_title[0].strip())
        # print(question_url[0])

        one_dict = {
            'pic': pic[0],
            'article_title': article_title[0].strip(),
            'article_author': article_author[0],
            'article_url': article_url[0],
            'question_title': question_title[0].strip(),
            'question_url': question_url[0]
        }
        print(one_dict)
        print(notes)
        return render(request, 'one.html', {'one_dict': one_dict,'notes':notes})
    except Exception as e :
        print(e)
        return render(request, 'one.html')



