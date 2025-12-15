from django.urls import path
from . import views

app_name = 'volunteers'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recommended/', views.recommended, name='recommended'),
    path('my-schedule/', views.my_schedule, name='my_schedule'),
    path('my-participation/', views.my_participation, name='my_participation'),
    path('log-hours/<int:opportunity_id>/', views.log_hours, name='log_hours'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]

