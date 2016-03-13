from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^results$', views.results, name='results'),
    url(r'^info$', views.info, name = 'info'),
    url(r'^d3-ski-resorts$', views.d3_ski_resorts, name ='d3-ski-resorts'),
]