"""journal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url,include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^journal_list/$', views.journal_list, name='journal_list'),
    url(r'^journal_add/$', views.journal_manage, name='journal_add'),
    url(r'^journal_edit/(?P<id>\d+)/$', views.journal_manage, name='journal_edit'),
    url(r'^approve/$', views.approve, name='approve'),
    url(r'^sheet_list/$', views.sheet_list, name='sheet_list'),
    url(r'^sheet_add/$', views.sheet_manage, name='sheet_add'),
    url(r'^sheet_edit/$', views.sheet_manage, name='sheet_edit'),
    url(r'^sheet_delete/$', views.sheet_manage, name='sheet_delete'),
]
