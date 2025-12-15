from django.contrib import admin
from .models import Opportunity, Application


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organisation', 'category', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'category', 'is_remote', 'created_at')
    search_fields = ('title', 'description', 'location', 'organisation__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'opportunity', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('volunteer__username', 'opportunity__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

