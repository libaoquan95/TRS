""" Photo.urls
"""
from django.urls import path
from . import views as photoView

urlpatterns = [
    path('upload/', photoView.uploadPhoto),
    path('list/<int:pageNum>/', photoView.getPhotosByUser),
    path('map/<int:photoId>/', photoView.getPhotoGeoById),
    path('delete/<int:photoId>/', photoView.deletePhotoById),
    path('<int:photoId>/', photoView.getPhotoById),
]
