from django.conf.urls import include, url
from west import views
urlpatterns = [
    url(r'main/',views.main),
    url(r'Bdanmaku2pic/',views.Bdanmaku2pic),
    url(r'pdf2String/',views.pdf2String),
    url(r'ip/',views.ip),
    url(r'porn/$',views.porn),
    url(r'porn/get_file_url$',views.get_file_url),
    url(r'request_info/$',views.request_info),

]