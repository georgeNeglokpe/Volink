"""
Unit tests for models.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import User
from organisations.models import Organisation
from opportunities.models import Opportunity, Application
from volunteers.models import VolunteerProfile, ParticipationRecord
from notifications.models import Notification


class ModelTests(TestCase):
    """Test model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
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
    
    def test_user_role_methods(self):
        """Test user role helper methods."""
        self.assertTrue(self.user.is_volunteer())
        self.assertFalse(self.user.is_org_admin())
        
        self.assertTrue(self.org_admin.is_org_admin())
        self.assertFalse(self.org_admin.is_volunteer())
    
    def test_organisation_creation(self):
        """Test organisation creation."""
        org = Organisation.objects.create(
            name='New Org',
            description='New org',
            contact_email='new@org.com',
            admin=self.org_admin
        )
        self.assertEqual(str(org), 'New Org')
        self.assertFalse(org.verified)  # Default should be False
    
    def test_opportunity_creation(self):
        """Test opportunity creation."""
        opp = Opportunity.objects.create(
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
        self.assertEqual(str(opp), 'Test Opportunity - Test Organisation')
        self.assertEqual(opp.status, 'OPEN')
    
    def test_volunteer_profile_creation(self):
        """Test volunteer profile creation."""
        profile = VolunteerProfile.objects.create(
            user=self.user,
            skills='Python',
            interests='Education',
            max_hours_per_week=10
        )
        self.assertEqual(str(profile), f'Profile for {self.user.username}')
    
    def test_application_creation(self):
        """Test application creation."""
        opp = Opportunity.objects.create(
            title='Test Opp',
            description='Test',
            location='Test',
            category='EDUCATION',
            required_skills='Python',
            min_hours_per_week=5,
            start_date='2024-01-01',
            end_date='2024-12-31',
            organisation=self.organisation
        )
        
        app = Application.objects.create(
            volunteer=self.user,
            opportunity=opp,
            status='PENDING'
        )
        self.assertEqual(str(app), f'{self.user.username} - Test Opp (PENDING)')
        self.assertEqual(app.status, 'PENDING')
    
    def test_notification_creation(self):
        """Test notification creation."""
        notification = Notification.objects.create(
            user=self.user,
            message='Test notification',
            type='SYSTEM'
        )
        self.assertIsNone(notification.read_at)
        self.assertEqual(str(notification), f'{self.user.username} - Test notification')
        
        # Test mark as read
        notification.mark_as_read()
        self.assertIsNotNone(notification.read_at)

