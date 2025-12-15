from django.contrib import admin
from .models import Organisation


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'contact_email', 'verified', 'created_at')
    list_filter = ('verified', 'created_at')
    search_fields = ('name', 'contact_email', 'admin__username')
    readonly_fields = ('created_at', 'updated_at')

