from django.urls import path
from . import views

urlpatterns = [
    path('ajax_data/', views.ajax_data),
    path('home/',views.form),
    path('detail_data/', views.result),
]