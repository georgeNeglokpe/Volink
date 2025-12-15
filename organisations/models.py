from django.db import models
from django.conf import settings


class Organisation(models.Model):
    """Organisation model representing NGOs and community organizations."""
    
    name = models.CharField(max_length=200, help_text='Organisation name')
    description = models.TextField(help_text='Detailed description of the organisation')
    contact_email = models.EmailField(help_text='Primary contact email')
    website = models.URLField(blank=True, null=True, help_text='Organisation website URL')
    verified = models.BooleanField(
        default=False,
        help_text='Whether the organisation has been verified by staff'
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organisations',
        help_text='Organisation administrator user'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['verified']),
            models.Index(fields=['admin']),
        ]
    
    def __str__(self):
        return self.name

