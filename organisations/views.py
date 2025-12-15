from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from .models import Organisation
from opportunities.models import Opportunity, Application
from volunteers.models import ParticipationRecord


def is_org_admin(user):
    """Check if user is an organisation admin."""
    return user.is_authenticated and user.is_org_admin()


@login_required
@user_passes_test(is_org_admin)
def dashboard(request):
    """Organisation admin dashboard."""
    # Get organisation(s) managed by this admin
    organisations = Organisation.objects.filter(admin=request.user)
    
    if not organisations.exists():
        return render(request, 'organisations/no_organisation.html', {
            'message': 'You are not associated with any organisation yet.'
        })
    
    # For now, show first organisation (can be extended for multiple)
    organisation = organisations.first()
    
    # Get opportunities for this organisation
    opportunities = Opportunity.objects.filter(organisation=organisation)
    
    # Calculate total hours per opportunity
    opportunity_stats = []
    for opp in opportunities:
        total_hours = ParticipationRecord.objects.filter(
            opportunity=opp
        ).aggregate(total=Sum('hours_logged'))['total'] or 0
        
        application_count = Application.objects.filter(opportunity=opp).count()
        accepted_count = Application.objects.filter(
            opportunity=opp,
            status='ACCEPTED'
        ).count()
        
        opportunity_stats.append({
            'opportunity': opp,
            'total_hours': total_hours,
            'application_count': application_count,
            'accepted_count': accepted_count,
        })
    
    # Calculate totals across all opportunities
    total_hours_contributed = sum(stat['total_hours'] for stat in opportunity_stats)
    total_applications = sum(stat['application_count'] for stat in opportunity_stats)
    
    context = {
        'organisation': organisation,
        'opportunities': opportunities,
        'opportunity_stats': opportunity_stats,
        'total_hours_contributed': total_hours_contributed,
        'total_applications': total_applications,
    }
    
    return render(request, 'organisations/dashboard.html', context)

