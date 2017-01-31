"""libraries_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from home.views import index
import django.contrib.auth.views

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^logout/$', django.contrib.auth.views.logout, name='logout', kwargs={'next_page': '/'}),
    url(r'^home/', include('home.urls')),
    url(r'^reader-cabinet/', include('reader_cabinet.urls')),
    url(r'^library-cabinet/', include('library_cabinet.urls')),
    url(r'^dnevnik-auth/', include('dnevnik_auth.urls')),
    url(r'^admin/', admin.site.urls),
]
