from django.conf.urls import url

from . import views

app_name = 'dnevnik_auth'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^import-cities/', views.import_cities, name='import_cities'),
]
