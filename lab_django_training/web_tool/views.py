from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

def hello_world(request):  # 看似沒有使用到參數request，但刪除則無法正常載入/hello/
    return HttpResponse("hello django!")


def hello_world2(request, username):
    now = datetime.now()
    return render(request, "hello.html", locals())

def get_time(request):
    time = datetime.now()  # 模板中需填入的變數可以透過url傳入，亦可使用function指定
    return render(request, "get_time.html", locals())
    # local()函數代表傳入所有區域變數，此例指time，若在url傳入參數亦是由local打包，如未傳入參數可省略