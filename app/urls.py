from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('playlist/<int:pk>', views.PlaylistDetailView, name='playlist'),
    path('recommend/<int:pk>', views.recommend, name='recommend'),
]