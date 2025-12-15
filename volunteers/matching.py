"""
Volunteer matching engine - matches volunteers to opportunities based on:
- Skills overlap
- Interests match
- Availability compatibility
- Location/remote preference
- Current workload
"""
from opportunities.models import Opportunity
from .scheduling import check_hours_limit


def calculate_skills_overlap(volunteer_skills, required_skills):
    """
    Calculate skills overlap score (0-1).
    Simple keyword matching approach.
    """
    if not volunteer_skills or not required_skills:
        return 0.0
    
    # Normalize to lowercase and split
    volunteer_skill_list = [s.strip().lower() for s in volunteer_skills.split(',')]
    required_skill_list = [s.strip().lower() for s in required_skills.split(',')]
    
    # Also check for skills in free text format
    volunteer_skills_text = volunteer_skills.lower()
    required_skills_text = required_skills.lower()
    
    # Count matches
    matches = 0
    total_required = len(required_skill_list) if required_skill_list else 1
    
    for req_skill in required_skill_list:
        if req_skill in volunteer_skill_list or req_skill in volunteer_skills_text:
            matches += 1
    
    # Return ratio (0-1)
    return min(matches / total_required, 1.0) if total_required > 0 else 0.0


def check_interests_match(volunteer_interests, opportunity_category):
    """
    Check if volunteer interests match opportunity category.
    Returns 1.0 if match, 0.0 otherwise.
    """
    if not volunteer_interests:
        return 0.0
    
    interests_lower = volunteer_interests.lower()
    category_lower = opportunity_category.lower()
    
    # Direct category match
    if category_lower in interests_lower:
        return 1.0
    
    # Keyword matching for common categories
    category_keywords = {
        'education': ['education', 'teaching', 'learning', 'tutoring'],
        'healthcare': ['health', 'medical', 'care', 'wellness'],
        'environment': ['environment', 'green', 'sustainability', 'climate'],
        'community': ['community', 'social', 'service', 'help'],
        'animals': ['animal', 'pet', 'wildlife', 'veterinary'],
        'arts': ['art', 'culture', 'creative', 'music', 'theater'],
        'sports': ['sport', 'fitness', 'exercise', 'athletic'],
        'technology': ['tech', 'computer', 'programming', 'digital'],
    }
    
    keywords = category_keywords.get(category_lower, [])
    for keyword in keywords:
        if keyword in interests_lower:
            return 1.0
    
    return 0.0


def check_availability_overlap(volunteer_availability, opportunity):
    """
    Check if volunteer availability overlaps with opportunity dates.
    Returns 1.0 if compatible, 0.0 otherwise.
    Simple date range check for now.
    """
    if not volunteer_availability:
        return 0.5  # Neutral score if no availability specified
    
    # Check if opportunity dates are in the future
    from django.utils import timezone
    today = timezone.now().date()
    
    if opportunity.start_date > today:
        # Opportunity is in the future, assume compatible if volunteer has availability set
        return 1.0
    
    # If opportunity has already started, check if it's still active
    if opportunity.end_date >= today:
        return 1.0
    
    return 0.0


def check_location_preference(volunteer_profile, opportunity):
    """
    Check location/remote preference match.
    For now, return 1.0 if remote opportunity (simplified).
    Can be extended with location matching.
    """
    # If volunteer hasn't specified preference, return neutral
    if not hasattr(volunteer_profile, 'availability') or not volunteer_profile.availability:
        return 0.5
    
    # If opportunity is remote, it's generally more flexible
    if opportunity.is_remote:
        return 1.0
    
    # For on-site opportunities, return neutral score
    return 0.5


def get_recommended_opportunities(volunteer_profile, limit=10):
    """
    Get ranked list of recommended opportunities for a volunteer.
    
    Args:
        volunteer_profile: VolunteerProfile instance
        limit: Maximum number of opportunities to return
    
    Returns:
        List of tuples (Opportunity, match_score)
    """
    # Get all open opportunities
    opportunities = Opportunity.objects.filter(status='OPEN')
    
    scored_opportunities = []
    
    for opp in opportunities:
        score = 0.0
        
        # Skills match (0-40 points)
        skills_match = calculate_skills_overlap(
            volunteer_profile.skills,
            opp.required_skills
        )
        score += skills_match * 40
        
        # Interests match (0-20 points)
        interests_match = check_interests_match(
            volunteer_profile.interests,
            opp.category
        )
        score += interests_match * 20
        
        # Availability compatibility (0-20 points)
        avail_match = check_availability_overlap(
            volunteer_profile.availability,
            opp
        )
        score += avail_match * 20
        
        # Location/remote preference (0-10 points)
        location_match = check_location_preference(volunteer_profile, opp)
        score += location_match * 10
        
        # Workload check - disqualify if would exceed limit
        can_apply, current_hours, would_be_hours = check_hours_limit(
            volunteer_profile.user,
            opp
        )
        if not can_apply:
            continue  # Skip if would exceed limit
        
        # Workload bonus (0-10 points) - prefer opportunities that fit well
        if current_hours + opp.min_hours_per_week <= volunteer_profile.max_hours_per_week:
            workload_score = 10.0
        else:
            workload_score = 5.0  # Partial fit
        score += workload_score
        
        scored_opportunities.append((opp, score))
    
    # Sort by score (descending) and return top results
    scored_opportunities.sort(key=lambda x: x[1], reverse=True)
    
    return scored_opportunities[:limit]

