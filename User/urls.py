""" User.urls
"""
from django.urls import path
from . import views as userView

urlpatterns = [
    path('login/', userView.login),
    path('logout/', userView.logout),
    path('register/', userView.register),
]
