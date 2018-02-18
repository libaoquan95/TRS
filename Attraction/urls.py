""" Photo.urls
"""
from django.urls import path
from . import views as attractionView

urlpatterns = [
    path('recommend/', attractionView.recommend),
    path('album/<int:provinceId>/<int:clusterId>/<int:pageNum>', attractionView.AttractionAlbum),
    path('map/<int:provinceId>/<int:clusterId>', attractionView.AttractionMap),
]
