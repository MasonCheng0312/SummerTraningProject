from django.urls import path
from . import views
from . import dataParser
from . import piRNA_target_predict



urlpatterns = [
    path('ajax_data/', views.ajax_data),
    path('home/',views.form),
    path('detail_data/', views.result),
    path('piRNA_taget_predict/', views.site),
    path('getData/', dataParser.getTransData),
    path('getPredictResult/', piRNA_target_predict.getPredictResult),
]