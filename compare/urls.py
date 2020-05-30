from . import views
from django.urls import include, path

urlpatterns = [
    path('', views.display_table, name='display_table'),
    #path('display/',views.display_table, name='display_table')
]