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
        print("except")
        return render(request, 'ip.html', {"my_ip": my_ip})
    return render(request, 'ip.html',{"my_ip":my_ip})