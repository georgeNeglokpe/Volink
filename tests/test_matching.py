"""
Unit tests for volunteer matching engine.
"""
from django.test import TestCase
from accounts.models import User
from organisations.models import Organisation
from opportunities.models import Opportunity
from volunteers.models import VolunteerProfile
from volunteers.matching import (
    calculate_skills_overlap,
    check_interests_match,
    check_availability_overlap,
    get_recommended_opportunities
)


class MatchingEngineTests(TestCase):
    """Test matching engine functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.volunteer_user = User.objects.create_user(
            username='testvolunteer',
            email='volunteer@test.com',
            password='testpass123',
            role='VOLUNTEER'
        )
        
        # Create volunteer profile
        self.profile = VolunteerProfile.objects.create(
            user=self.volunteer_user,
            skills='Python, JavaScript, Teaching',
            interests='Education, Technology',
            max_hours_per_week=10,
            availability={'monday': '9-17', 'wednesday': '9-17'}
        )
        
        # Create organisation
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
    
    def test_skills_overlap_exact_match(self):
        """Test skills overlap with exact matches."""
        score = calculate_skills_overlap('Python, JavaScript', 'Python, JavaScript')
        self.assertGreater(score, 0.8)
    
    def test_skills_overlap_partial_match(self):
        """Test skills overlap with partial matches."""
        score = calculate_skills_overlap('Python, JavaScript', 'Python, C++')
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)
    
    def test_skills_overlap_no_match(self):
        """Test skills overlap with no matches."""
        score = calculate_skills_overlap('Python', 'Cooking, Gardening')
        self.assertEqual(score, 0.0)
    
    def test_interests_match(self):
        """Test interests matching."""
        score = check_interests_match('Education, Technology', 'EDUCATION')
        self.assertEqual(score, 1.0)
    
    def test_interests_no_match(self):
        """Test interests with no match."""
        score = check_interests_match('Sports', 'EDUCATION')
        self.assertEqual(score, 0.0)
    
    def test_availability_overlap(self):
        """Test availability overlap check."""
        opp = Opportunity.objects.create(
            title='Test Opp',
            description='Test',
            location='Test Location',
            category='EDUCATION',
            required_skills='Python',
            min_hours_per_week=5,
            start_date='2024-01-01',
            end_date='2024-12-31',
            organisation=self.organisation
        )
        score = check_availability_overlap(self.profile.availability, opp)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_get_recommended_opportunities(self):
        """Test getting recommended opportunities."""
        # Create opportunity
        opp = Opportunity.objects.create(
            title='Python Teaching',
            description='Teach Python',
            location='Remote',
            category='EDUCATION',
            required_skills='Python, Teaching',
            min_hours_per_week=5,
            start_date='2024-01-01',
            end_date='2024-12-31',
            is_remote=True,
            organisation=self.organisation
        )
        
        recommendations = get_recommended_opportunities(self.profile, limit=10)
        self.assertGreater(len(recommendations), 0)
        self.assertEqual(recommendations[0][0], opp)  # Should be first recommendation

