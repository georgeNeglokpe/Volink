"""
Scheduling and availability logic for volunteers.
Handles hours limit checking and schedule calculation.
"""
from opportunities.models import Application


def check_hours_limit(volunteer, new_opportunity):
    """
    Check if adding a new opportunity would exceed volunteer's max hours per week.
    
    Args:
        volunteer: User instance (volunteer)
        new_opportunity: Opportunity instance
    
    Returns:
        Tuple: (can_apply: bool, current_hours: int, would_be_hours: int)
    """
    from .models import VolunteerProfile
    
    try:
        profile = volunteer.volunteer_profile
    except VolunteerProfile.DoesNotExist:
        # No profile yet, allow application
        return (True, 0, new_opportunity.min_hours_per_week)
    
    max_hours = profile.max_hours_per_week
    
    # Get all accepted applications
    accepted_applications = Application.objects.filter(
        volunteer=volunteer,
        status='ACCEPTED'
    )
    
    # Calculate current total hours
    current_hours = sum(
        app.opportunity.min_hours_per_week
        for app in accepted_applications
    )
    
    # Calculate would-be hours
    would_be_hours = current_hours + new_opportunity.min_hours_per_week
    
    # Check if would exceed limit
    can_apply = would_be_hours <= max_hours
    
    return (can_apply, current_hours, would_be_hours)


def get_volunteer_schedule(volunteer):
    """
    Get volunteer's current schedule with active opportunities and estimated hours.
    
    Args:
        volunteer: User instance (volunteer)
    
    Returns:
        Dict with schedule information
    """
    from .models import VolunteerProfile
    
    try:
        profile = volunteer.volunteer_profile
    except VolunteerProfile.DoesNotExist:
        return {
            'opportunities': [],
            'total_hours': 0,
            'max_hours': 0,
            'remaining_capacity': 0,
        }
    
    # Get all accepted applications
    accepted_applications = Application.objects.filter(
        volunteer=volunteer,
        status='ACCEPTED'
    ).select_related('opportunity')
    
    opportunities = []
    total_hours = 0
    
    for app in accepted_applications:
        opp = app.opportunity
        hours = opp.min_hours_per_week
        opportunities.append({
            'opportunity': opp,
            'application': app,
            'hours_per_week': hours,
            'start_date': opp.start_date,
            'end_date': opp.end_date,
        })
        total_hours += hours
    
    return {
        'opportunities': opportunities,
        'total_hours': total_hours,
        'max_hours': profile.max_hours_per_week,
        'remaining_capacity': profile.max_hours_per_week - total_hours,
    }

