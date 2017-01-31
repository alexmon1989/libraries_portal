from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login, name='login'),
    url(r'^user-register/', views.user_register, name='user_register'),
    url(r'^library-register/', views.library_register, name='library_register'),
    url(r'^get-cities/(?P<region_id>[0-9]+)/$', views.get_cities),
    url(r'^get-library-kinds/(?P<library_type_id>[0-9]+)/$', views.get_library_kinds),
    url(r'^get-libraries-in-city/(?P<city_id>[0-9]+)/$', views.get_libraries_in_city),
]
