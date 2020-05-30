from . import views
from django.urls import include, path

urlpatterns = [
    path('', views.model_upload, name='model_upload'),
    path('filters/', include(('compare.urls', 'compare'), namespace='compare'))
]