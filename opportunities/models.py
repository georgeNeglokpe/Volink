from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from organisations.models import Organisation


class Opportunity(models.Model):
    """Volunteering opportunity posted by organisations."""
    
    CATEGORY_CHOICES = [
        ('EDUCATION', 'Education'),
        ('HEALTHCARE', 'Healthcare'),
        ('ENVIRONMENT', 'Environment'),
        ('COMMUNITY', 'Community Service'),
        ('ANIMALS', 'Animals'),
        ('ARTS', 'Arts & Culture'),
        ('SPORTS', 'Sports & Recreation'),
        ('TECHNOLOGY', 'Technology'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]
    
    title = models.CharField(max_length=200, help_text='Opportunity title')
    description = models.TextField(help_text='Detailed description of the opportunity')
    location = models.CharField(max_length=200, help_text='Location of the opportunity')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='OTHER',
        help_text='Category of the opportunity'
    )
    required_skills = models.TextField(
        help_text='Required skills (comma-separated or free text)'
    )
    min_hours_per_week = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text='Minimum hours per week required'
    )
    start_date = models.DateField(help_text='Start date of the opportunity')
    end_date = models.DateField(help_text='End date of the opportunity')
    is_remote = models.BooleanField(
        default=False,
        help_text='Whether this is a remote opportunity'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='OPEN',
        help_text='Current status of the opportunity'
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='opportunities',
        help_text='Organisation posting this opportunity'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Opportunities'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['location']),
            models.Index(fields=['organisation']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.organisation.name}"
    
    def clean(self):
        """Validate that end_date is after start_date."""
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({'end_date': 'End date must be after start date.'})
    
    def save(self, *args, **kwargs):
        """Override save to call clean."""
        self.full_clean()
        super().save(*args, **kwargs)


class Application(models.Model):
    """Application by a volunteer to an opportunity."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text='Volunteer applying'
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text='Opportunity being applied to'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text='Application status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['volunteer', 'opportunity']  # One application per volunteer per opportunity
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['volunteer']),
            models.Index(fields=['opportunity']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.volunteer.username} - {self.opportunity.title} ({self.status})"

