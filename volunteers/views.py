from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django import forms
from .models import VolunteerProfile, ParticipationRecord
from .matching import get_recommended_opportunities
from .scheduling import get_volunteer_schedule
from opportunities.models import Opportunity, Application


def is_volunteer(user):
    """Check if user is a volunteer."""
    return user.is_authenticated and user.is_volunteer()


@login_required
@user_passes_test(is_volunteer)
def dashboard(request):
    """Volunteer dashboard with summary."""
    volunteer = request.user
    
    # Get or create volunteer profile
    profile, created = VolunteerProfile.objects.get_or_create(user=volunteer)
    
    # Get total hours logged
    total_hours = ParticipationRecord.objects.filter(
        volunteer=volunteer
    ).aggregate(total=Sum('hours_logged'))['total'] or 0
    
    # Get hours by opportunity
    hours_by_opportunity = ParticipationRecord.objects.filter(
        volunteer=volunteer
    ).values('opportunity__title').annotate(
        total_hours=Sum('hours_logged')
    ).order_by('-total_hours')[:10]
    
    # Get recent participation records
    recent_records = ParticipationRecord.objects.filter(
        volunteer=volunteer
    ).select_related('opportunity').order_by('-date', '-created_at')[:10]
    
    # Get active applications
    active_applications = Application.objects.filter(
        volunteer=volunteer,
        status__in=['PENDING', 'ACCEPTED']
    ).select_related('opportunity').order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'total_hours': total_hours,
        'hours_by_opportunity': hours_by_opportunity,
        'recent_records': recent_records,
        'active_applications': active_applications,
    }
    return render(request, 'volunteers/dashboard.html', context)


@login_required
@user_passes_test(is_volunteer)
def recommended(request):
    """Recommended opportunities for the volunteer."""
    volunteer = request.user
    
    # Get or create volunteer profile
    profile, created = VolunteerProfile.objects.get_or_create(user=volunteer)
    
    # Get recommended opportunities
    recommendations = get_recommended_opportunities(profile, limit=20)
    
    # Check which opportunities user has already applied to
    applied_opportunity_ids = set(
        Application.objects.filter(volunteer=volunteer).values_list('opportunity_id', flat=True)
    )
    
    context = {
        'recommendations': recommendations,
        'applied_opportunity_ids': applied_opportunity_ids,
    }
    return render(request, 'volunteers/recommended.html', context)


@login_required
@user_passes_test(is_volunteer)
def my_schedule(request):
    """Volunteer's current schedule."""
    volunteer = request.user
    schedule = get_volunteer_schedule(volunteer)
    
    context = {
        'schedule': schedule,
    }
    return render(request, 'volunteers/my_schedule.html', context)


@login_required
@user_passes_test(is_volunteer)
def my_participation(request):
    """Volunteer's participation tracking page."""
    volunteer = request.user
    
    # Get all participation records
    records = ParticipationRecord.objects.filter(
        volunteer=volunteer
    ).select_related('opportunity').order_by('-date', '-created_at')
    
    # Get total hours
    total_hours = ParticipationRecord.objects.filter(
        volunteer=volunteer
    ).aggregate(total=Sum('hours_logged'))['total'] or 0
    
    # Get hours by opportunity for chart
    hours_by_opportunity = ParticipationRecord.objects.filter(
        volunteer=volunteer
    ).values('opportunity__title', 'opportunity__id').annotate(
        total_hours=Sum('hours_logged')
    ).order_by('-total_hours')
    
    context = {
        'records': records,
        'total_hours': total_hours,
        'hours_by_opportunity': hours_by_opportunity,
    }
    return render(request, 'volunteers/my_participation.html', context)


@login_required
@user_passes_test(is_volunteer)
def log_hours(request, opportunity_id):
    """Log hours for a specific opportunity."""
    opportunity = get_object_or_404(Opportunity, pk=opportunity_id)
    volunteer = request.user
    
    # Check if volunteer has accepted application for this opportunity
    has_application = Application.objects.filter(
        volunteer=volunteer,
        opportunity=opportunity,
        status='ACCEPTED'
    ).exists()
    
    if not has_application:
        messages.error(request, 'You must have an accepted application to log hours for this opportunity.')
        return redirect('volunteers:my_participation')
    
    if request.method == 'POST':
        hours = request.POST.get('hours_logged')
        date = request.POST.get('date')
        notes = request.POST.get('notes', '')
        
        try:
            hours_float = float(hours)
            if hours_float <= 0:
                raise ValueError('Hours must be positive')
            
            record = ParticipationRecord.objects.create(
                volunteer=volunteer,
                opportunity=opportunity,
                hours_logged=hours_float,
                date=date,
                notes=notes
            )
            messages.success(request, f'Successfully logged {hours_float} hours!')
            return redirect('volunteers:my_participation')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Invalid input: {str(e)}')
    
    context = {
        'opportunity': opportunity,
    }
    return render(request, 'volunteers/log_hours.html', context)


@login_required
@user_passes_test(is_volunteer)
def edit_profile(request):
    """Edit volunteer profile."""
    volunteer = request.user
    profile, created = VolunteerProfile.objects.get_or_create(user=volunteer)
    
    if request.method == 'POST':
        profile.skills = request.POST.get('skills', '')
        profile.interests = request.POST.get('interests', '')
        profile.max_hours_per_week = int(request.POST.get('max_hours_per_week', 10))
        
        # Handle availability (simplified - can be enhanced)
        # For now, just store as JSON
        availability = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            if request.POST.get(f'availability_{day}'):
                availability[day] = request.POST.get(f'time_{day}', '')
        profile.availability = availability
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('volunteers:dashboard')
    
    context = {
        'profile': profile,
    }
    return render(request, 'volunteers/edit_profile.html', context)

