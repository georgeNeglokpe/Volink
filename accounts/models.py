from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model extending AbstractUser."""
    
    ROLE_CHOICES = [
        ('VOLUNTEER', 'Volunteer'),
        ('ORGANISATION_ADMIN', 'Organisation Admin'),
        ('STAFF_ADMIN', 'Staff Admin'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='VOLUNTEER',
        help_text='User role in the system'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    course_department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Course or department (for students)'
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_volunteer(self):
        """Check if user is a volunteer."""
        return self.role == 'VOLUNTEER'
    
    def is_org_admin(self):
        """Check if user is an organisation admin."""
        return self.role == 'ORGANISATION_ADMIN'
    
    def is_staff_admin(self):
        """Check if user is a staff admin."""
        return self.role == 'STAFF_ADMIN'

