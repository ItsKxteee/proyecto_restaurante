from django.urls import path
from . import views

urlpatterns = [
    path('carta/', views.ver_carta, name='ver_carta'),
]