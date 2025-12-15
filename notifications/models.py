from django.db import models
from django.conf import settings


class Notification(models.Model):
    """In-app notifications for users."""
    
    TYPE_CHOICES = [
        ('SYSTEM', 'System'),
        ('OPPORTUNITY_UPDATE', 'Opportunity Update'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='User who receives the notification'
    )
    message = models.TextField(help_text='Notification message')
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='SYSTEM',
        help_text='Type of notification'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, help_text='When the notification was read')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['read_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        if not self.read_at:
            self.read_at = timezone.now()
            self.save()

