from django.urls import path
from . import views

app_name = 'organisations'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]

