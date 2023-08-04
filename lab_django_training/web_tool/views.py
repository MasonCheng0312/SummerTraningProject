from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from web_tool.models import Gene
import pandas as pd
import json

def hello_world(request):  # 看似沒有使用到參數request，但刪除則無法正常載入/hello/
    return HttpResponse("hello django!")


def hello_world2(request, username):
    now = datetime.now()
    return render(request, "hello.html", locals())

def get_time(request):
    time = datetime.now()  # 模板中需填入的變數可以透過url傳入，亦可使用function指定
    return render(request, "get_time.html", locals())
    # local()函數代表傳入所有區域變數，此例指time，若在url傳入參數亦是由local打包，如未傳入參數可省略


def index(request):
    df = pd.read_csv("/home/cosbi2/py_project/summer_training/lab_django_training/data/hw1_output.csv")
    df = df.head(100)
    df = df.rename(columns={"Gene_ID":"id", "transcript_ID": "transcript", "# of transcripts": "number"})

    json_string = df.to_json(orient='records')

    genes = json.loads(json_string)
    # 將json資料格式轉成python認識的資料結構，此處為字典

    return render(request, "index.html", locals())


def printer(request):
    test_objects = Gene.objects.filter(gene_id__contains = "WBGene0000001")
    return render(request, "test.html", locals())





