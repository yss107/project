"""
URL configuration for the sensing app
"""
from django.urls import path
from . import views

app_name = 'sensing'

urlpatterns = [
    path('', views.index, name='index'),
    path('images/', views.SatelliteImageListView.as_view(), name='image_list'),
    path('images/<int:pk>/', views.SatelliteImageDetailView.as_view(), name='image_detail'),
    path('dataset-info/', views.dataset_info, name='dataset_info'),
    path('about/', views.about, name='about'),
]
