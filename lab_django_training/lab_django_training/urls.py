"""
URL configuration for lab_django_training project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from web_tool import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', views.hello_world),
    path('time/', views.get_time),
    path('hello/<str:username>',views.hello_world2),
    # 雖然都是hello/，但後面加上參數傳入的url似乎與前一個是不同的，網頁能夠清楚分辨兩者差異。
    # 記得在使用參數傳入時寫法，型態後面不可以+空格！！！會導致error
    path('web_tool/', include("web_tool.urls")),
]
