from django.contrib import admin
from .models import VolunteerProfile, ParticipationRecord


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'max_hours_per_week', 'created_at')
    search_fields = ('user__username', 'user__email', 'skills', 'interests')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ParticipationRecord)
class ParticipationRecordAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'opportunity', 'hours_logged', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('volunteer__username', 'opportunity__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'

