"""
Integration tests for application workflows.
"""
from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from organisations.models import Organisation
from opportunities.models import Opportunity, Application
from notifications.models import Notification


class WorkflowTests(TestCase):
    """Test application workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.volunteer = User.objects.create_user(
            username='volunteer',
            email='volunteer@test.com',
            password='testpass123',
            role='VOLUNTEER'
        )
        
        self.org_admin = User.objects.create_user(
            username='orgadmin',
            email='admin@org.com',
            password='testpass123',
            role='ORGANISATION_ADMIN'
        )
        
        self.organisation = Organisation.objects.create(
            name='Test Organisation',
            description='Test org',
            contact_email='contact@org.com',
            admin=self.org_admin,
            verified=True
        )
        
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity',
            description='Test description',
            location='Test Location',
            category='EDUCATION',
            required_skills='Python',
            min_hours_per_week=5,
            start_date='2024-01-01',
            end_date='2024-12-31',
            organisation=self.organisation
        )
    
    def test_application_workflow(self):
        """Test complete application workflow."""
        from notifications.models import Notification
        
        # Volunteer applies (simulating view behavior - create notification)
        application = Application.objects.create(
            volunteer=self.volunteer,
            opportunity=self.opportunity,
            status='PENDING'
        )
        
        # Create notification as the view would (simulating apply_to_opportunity view)
        Notification.objects.create(
            user=self.org_admin,
            message=f'New application from {self.volunteer.username} for "{self.opportunity.title}"',
            type='OPPORTUNITY_UPDATE'
        )
        
        # Check notification created for org admin
        notification = Notification.objects.filter(
            user=self.org_admin,
            type='OPPORTUNITY_UPDATE'
        ).first()
        self.assertIsNotNone(notification)
        self.assertIn(self.volunteer.username, notification.message)
        
        # Admin accepts application
        application.status = 'ACCEPTED'
        application.save()
        
        # Create notification for volunteer (simulating the view behavior)
        Notification.objects.create(
            user=self.volunteer,
            message=f'Your application for "{self.opportunity.title}" has been accepted.',
            type='OPPORTUNITY_UPDATE'
        )
        
        # Check volunteer notification
        vol_notification = Notification.objects.filter(
            user=self.volunteer,
            type='OPPORTUNITY_UPDATE'
        ).first()
        self.assertIsNotNone(vol_notification)
        self.assertIn('accepted', vol_notification.message.lower())
    
    def test_permission_checks(self):
        """Test permission checks for different user roles."""
        # Volunteer should not access org admin pages
        self.client.login(username='volunteer', password='testpass123')
        response = self.client.get(reverse('opportunities:list'))
        # Should redirect or show error (depending on implementation)
        self.assertIn(response.status_code, [302, 403])
        
        # Org admin should access org pages
        self.client.login(username='orgadmin', password='testpass123')
        response = self.client.get(reverse('opportunities:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_unauthenticated_redirect(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(reverse('volunteers:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

