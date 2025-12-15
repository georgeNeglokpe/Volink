"""
Unit tests for scheduling and availability logic.
"""
from django.test import TestCase
from accounts.models import User
from organisations.models import Organisation
from opportunities.models import Opportunity, Application
from volunteers.models import VolunteerProfile
from volunteers.scheduling import check_hours_limit, get_volunteer_schedule


class SchedulingTests(TestCase):
    """Test scheduling logic."""
    
    def setUp(self):
        """Set up test data."""
        self.volunteer_user = User.objects.create_user(
            username='testvolunteer',
            email='volunteer@test.com',
            password='testpass123',
            role='VOLUNTEER'
        )
        
        self.profile = VolunteerProfile.objects.create(
            user=self.volunteer_user,
            skills='Python',
            interests='Education',
            max_hours_per_week=10,
            availability={}
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
    
    def test_hours_limit_within_limit(self):
        """Test hours limit check when within limit."""
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
        
        can_apply, current_hours, would_be_hours = check_hours_limit(
            self.volunteer_user,
            opp
        )
        
        self.assertTrue(can_apply)
        self.assertEqual(current_hours, 0)
        self.assertEqual(would_be_hours, 5)
    
    def test_hours_limit_exceeds_limit(self):
        """Test hours limit check when exceeds limit."""
        # Create opportunity that would exceed limit
        opp = Opportunity.objects.create(
            title='Test Opp',
            description='Test',
            location='Test',
            category='EDUCATION',
            required_skills='Python',
            min_hours_per_week=15,  # Exceeds max of 10
            start_date='2024-01-01',
            end_date='2024-12-31',
            organisation=self.organisation
        )
        
        can_apply, current_hours, would_be_hours = check_hours_limit(
            self.volunteer_user,
            opp
        )
        
        self.assertFalse(can_apply)
    
    def test_hours_limit_with_existing_applications(self):
        """Test hours limit with existing accepted applications."""
        # Create and accept first opportunity
        opp1 = Opportunity.objects.create(
            title='Opp 1',
            description='Test',
            location='Test',
            category='EDUCATION',
            required_skills='Python',
            min_hours_per_week=6,
            start_date='2024-01-01',
            end_date='2024-12-31',
            organisation=self.organisation
        )
        Application.objects.create(
            volunteer=self.volunteer_user,
            opportunity=opp1,
            status='ACCEPTED'
        )
        
        # Try to add second opportunity
        opp2 = Opportunity.objects.create(
            title='Opp 2',
            description='Test',
            location='Test',
            category='EDUCATION',
            required_skills='Python',
            min_hours_per_week=5,
            start_date='2024-01-01',
            end_date='2024-12-31',
            organisation=self.organisation
        )
        
        can_apply, current_hours, would_be_hours = check_hours_limit(
            self.volunteer_user,
            opp2
        )
        
        # 6 + 5 = 11 > 10 (max), so should be prevented
        self.assertFalse(can_apply)
        self.assertEqual(current_hours, 6)
        self.assertEqual(would_be_hours, 11)
    
    def test_get_volunteer_schedule(self):
        """Test getting volunteer schedule."""
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
        
        Application.objects.create(
            volunteer=self.volunteer_user,
            opportunity=opp,
            status='ACCEPTED'
        )
        
        schedule = get_volunteer_schedule(self.volunteer_user)
        
        self.assertEqual(len(schedule['opportunities']), 1)
        self.assertEqual(schedule['total_hours'], 5)
        self.assertEqual(schedule['max_hours'], 10)

