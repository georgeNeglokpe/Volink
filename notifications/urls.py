from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.list_notifications, name='list'),
    path('<int:notification_id>/read/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('count/', views.notification_count, name='count'),
]

