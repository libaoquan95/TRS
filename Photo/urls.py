""" Photo.urls
"""
from django.urls import path
from . import views as photoView

urlpatterns = [
    path('upload/', photoView.uploadPhoto),
    path('myphotos/<int:pageNum>/', photoView.getPhotosByUser),
    path('<int:photoId>/', photoView.getPhotoById),
    path('map/<int:photoId>/', photoView.getPhotoGeoById),
]
