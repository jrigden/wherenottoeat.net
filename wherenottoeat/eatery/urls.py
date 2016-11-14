from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^inspection/(?P<slug>[\w-]+)', views.inspection_detail, name='inspection_detail'),
    url(r'^restaurant/(?P<slug>[\w-]+)', views.restaurant_detail, name='restaurant_detail'),
    url(r'^location/(?P<radius>[\d+\.\d+-]+)/(?P<lat>[\d+\.\d+-]+)/(?P<lng>[\d+\.\d+-]+)', views.location, name='location'),
    url(r'^', views.locate, name='locate'),
    #url(r'^', views.index, name='index'),
]
