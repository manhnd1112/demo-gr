from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.Views.index, name="index"),
    path('ajax/test', views.Ajax.test, name="test"),
    path('ajax/mape', views.Ajax.mape, name="mape")
]