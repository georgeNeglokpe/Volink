from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from opportunities.models import Opportunity


class VolunteerProfile(models.Model):
    """Extended profile for volunteer users."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='volunteer_profile',
        help_text='Associated user account'
    )
    skills = models.TextField(
        help_text='Skills and qualifications (comma-separated or free text)'
    )
    availability = models.JSONField(
        default=dict,
        help_text='Availability schedule (JSON format: days/times)'
    )
    interests = models.TextField(
        help_text='Interests and preferences (comma-separated or free text)'
    )
    max_hours_per_week = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text='Maximum hours per week the volunteer can commit'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Profile for {self.user.username}"


class ParticipationRecord(models.Model):
    """Record of hours logged by volunteers."""
    
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participation_records',
        help_text='Volunteer who logged the hours'
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='participation_records',
        help_text='Opportunity for which hours were logged'
    )
    hours_logged = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Hours logged'
    )
    date = models.DateField(help_text='Date of participation')
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Optional notes about the participation'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['volunteer']),
            models.Index(fields=['opportunity']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.volunteer.username} - {self.opportunity.title} - {self.hours_logged}h on {self.date}"

