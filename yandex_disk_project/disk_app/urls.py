from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница приложения
    path('download/', views.download_files, name='download_files'), # Маршрут для скачивагия
]
