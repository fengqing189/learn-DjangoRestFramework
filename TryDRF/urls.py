"""TryDRF URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url

from app02 import views as app02_view

urlpatterns = [
    url(r'login/',app02_view.LoginView.as_view()),
    url(r'host/',app02_view.HostView.as_view()),
    url(r'users/',app02_view.Users.as_view()),
    url(r'salary/',app02_view.Salary.as_view()),
    url(r'index/',app02_view.IndexView.as_view()),

]
