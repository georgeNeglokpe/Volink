from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    path('', views.browse_opportunities, name='browse'),
    path('<int:pk>/', views.opportunity_detail, name='detail'),
    path('<int:pk>/apply/', views.apply_to_opportunity, name='apply'),
    path('my-opportunities/', views.list_opportunities, name='list'),
    path('create/', views.create_opportunity, name='create'),
    path('<int:pk>/edit/', views.edit_opportunity, name='edit'),
    path('<int:pk>/delete/', views.delete_opportunity, name='delete'),
    path('<int:pk>/applications/', views.view_applications, name='applications'),
    path('applications/<int:application_id>/status/<str:new_status>/', views.update_application_status, name='update_status'),
]

