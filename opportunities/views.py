from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Q
from django import forms
from .models import Opportunity, Application
from .forms import OpportunityForm, ApplicationForm
from organisations.models import Organisation
from notifications.models import Notification
from volunteers.scheduling import check_hours_limit, get_volunteer_schedule


def is_org_admin(user):
    """Check if user is an organisation admin."""
    return user.is_authenticated and user.is_org_admin()


def is_volunteer(user):
    """Check if user is a volunteer."""
    return user.is_authenticated and user.is_volunteer()


def browse_opportunities(request):
    """Browse all open opportunities with filters."""
    opportunities = Opportunity.objects.filter(status='OPEN')
    
    # Filtering
    category = request.GET.get('category')
    location = request.GET.get('location')
    is_remote = request.GET.get('is_remote')
    search = request.GET.get('search')
    
    if category:
        opportunities = opportunities.filter(category=category)
    if location:
        opportunities = opportunities.filter(location__icontains=location)
    if is_remote:
        opportunities = opportunities.filter(is_remote=(is_remote == 'true'))
    if search:
        opportunities = opportunities.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    # Get user's applications if logged in
    user_applications = {}
    if request.user.is_authenticated:
        user_applications = {
            app.opportunity_id: app.status
            for app in Application.objects.filter(volunteer=request.user)
        }
    
    context = {
        'opportunities': opportunities,
        'user_applications': user_applications,
        'categories': Opportunity.CATEGORY_CHOICES,
    }
    return render(request, 'opportunities/browse.html', context)


def opportunity_detail(request, pk):
    """View details of a specific opportunity."""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Check if user has applied
    user_application = None
    hours_limit_info = None
    if request.user.is_authenticated:
        try:
            user_application = Application.objects.get(
                volunteer=request.user,
                opportunity=opportunity
            )
        except Application.DoesNotExist:
            pass
        
        # Check hours limit for volunteers (to show warning if applicable)
        if request.user.is_volunteer() and not user_application:
            can_apply, current_hours, would_be_hours = check_hours_limit(request.user, opportunity)
            try:
                profile = request.user.volunteer_profile
                max_hours = profile.max_hours_per_week
            except:
                max_hours = 0
            
            hours_limit_info = {
                'can_apply': can_apply,
                'current_hours': current_hours,
                'would_be_hours': would_be_hours,
                'max_hours': max_hours,
            }
    
    context = {
        'opportunity': opportunity,
        'user_application': user_application,
        'hours_limit_info': hours_limit_info,
    }
    return render(request, 'opportunities/detail.html', context)


@login_required
@user_passes_test(is_volunteer)
def apply_to_opportunity(request, pk):
    """Volunteer applies to an opportunity."""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Check if already applied
    if Application.objects.filter(volunteer=request.user, opportunity=opportunity).exists():
        messages.warning(request, 'You have already applied to this opportunity.')
        return redirect('opportunities:detail', pk=pk)
    
    # Check if opportunity is open
    if opportunity.status != 'OPEN':
        messages.error(request, 'This opportunity is not currently open for applications.')
        return redirect('opportunities:detail', pk=pk)
    
    # Check hours limit before allowing application
    can_apply, current_hours, would_be_hours = check_hours_limit(request.user, opportunity)
    if not can_apply:
        try:
            profile = request.user.volunteer_profile
            max_hours = profile.max_hours_per_week
        except:
            max_hours = 0
        
        messages.error(
            request,
            f'Cannot apply: This opportunity would exceed your weekly hours limit. '
            f'You currently have {current_hours} hours/week committed (max: {max_hours} hours/week). '
            f'This opportunity requires {opportunity.min_hours_per_week} hours/week, '
            f'which would bring you to {would_be_hours} hours/week.'
        )
        return redirect('opportunities:detail', pk=pk)
    
    if request.method == 'POST':
        application = Application.objects.create(
            volunteer=request.user,
            opportunity=opportunity,
            status='PENDING'
        )
        
        # Create notification for organisation admin
        Notification.objects.create(
            user=opportunity.organisation.admin,
            message=f'New application from {request.user.username} for "{opportunity.title}"',
            type='OPPORTUNITY_UPDATE'
        )
        
        messages.success(request, 'Application submitted successfully!')
        return redirect('opportunities:detail', pk=pk)
    
    return redirect('opportunities:detail', pk=pk)


@login_required
@user_passes_test(is_org_admin)
def list_opportunities(request):
    """List all opportunities for the organisation admin."""
    # Get organisation(s) managed by this admin
    organisations = Organisation.objects.filter(admin=request.user)
    
    if not organisations.exists():
        messages.warning(request, 'You are not associated with any organisation.')
        return redirect('organisations:dashboard')
    
    # Get opportunities for all organisations managed by this admin
    opportunities = Opportunity.objects.filter(organisation__in=organisations)
    
    context = {
        'opportunities': opportunities,
    }
    return render(request, 'opportunities/my_opportunities.html', context)


@login_required
@user_passes_test(is_org_admin)
def create_opportunity(request):
    """Create a new opportunity."""
    organisations = Organisation.objects.filter(admin=request.user)
    
    if not organisations.exists():
        messages.error(request, 'You must be associated with an organisation to create opportunities.')
        return redirect('organisations:dashboard')
    
    if request.method == 'POST':
        form = OpportunityForm(request.POST, user=request.user)
        if form.is_valid():
            opportunity = form.save(commit=False)
            # Set organisation from form or first available
            if 'organisation' in form.cleaned_data:
                opportunity.organisation = form.cleaned_data['organisation']
            else:
                opportunity.organisation = organisations.first()
            opportunity.save()
            messages.success(request, 'Opportunity created successfully!')
            return redirect('opportunities:list')
    else:
        form = OpportunityForm(user=request.user)
        if organisations.count() == 1:
            form.fields['organisation'] = forms.ModelChoiceField(
                queryset=organisations,
                initial=organisations.first(),
                widget=forms.HiddenInput()
            )
    
    context = {
        'form': form,
    }
    return render(request, 'opportunities/opportunity_form.html', context)


@login_required
@user_passes_test(is_org_admin)
def edit_opportunity(request, pk):
    """Edit an existing opportunity."""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Check if user manages this opportunity's organisation
    if opportunity.organisation.admin != request.user:
        messages.error(request, 'You do not have permission to edit this opportunity.')
        return redirect('opportunities:list')
    
    if request.method == 'POST':
        form = OpportunityForm(request.POST, instance=opportunity, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Opportunity updated successfully!')
            return redirect('opportunities:list')
    else:
        form = OpportunityForm(instance=opportunity, user=request.user)
    
    context = {
        'form': form,
        'opportunity': opportunity,
    }
    return render(request, 'opportunities/opportunity_form.html', context)


@login_required
@user_passes_test(is_org_admin)
def delete_opportunity(request, pk):
    """Delete an opportunity."""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Check if user manages this opportunity's organisation
    if opportunity.organisation.admin != request.user:
        messages.error(request, 'You do not have permission to delete this opportunity.')
        return redirect('opportunities:list')
    
    if request.method == 'POST':
        opportunity.delete()
        messages.success(request, 'Opportunity deleted successfully!')
        return redirect('opportunities:list')
    
    context = {
        'opportunity': opportunity,
    }
    return render(request, 'opportunities/delete_confirm.html', context)


@login_required
@user_passes_test(is_org_admin)
def view_applications(request, pk):
    """View applications for a specific opportunity."""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Check if user manages this opportunity's organisation
    if opportunity.organisation.admin != request.user:
        messages.error(request, 'You do not have permission to view these applications.')
        return redirect('opportunities:list')
    
    applications = Application.objects.filter(opportunity=opportunity).select_related('volunteer', 'volunteer__volunteer_profile').order_by('-created_at')
    
    # Calculate hours information for each application
    applications_with_hours = []
    for application in applications:
        volunteer = application.volunteer
        schedule = get_volunteer_schedule(volunteer)
        
        current_hours = schedule['total_hours']
        max_hours = schedule['max_hours']
        remaining_hours = schedule.get('remaining_capacity', max_hours - current_hours)
        
        # Calculate what hours would be if this application is accepted
        hours_for_this = opportunity.min_hours_per_week
        if application.status == 'ACCEPTED':
            # If already accepted, current_hours already includes this opportunity
            would_be_hours = current_hours
        else:
            # If pending/rejected, calculate what it would be if accepted
            would_be_hours = current_hours + hours_for_this
        
        # Check if accepting would exceed limit
        would_exceed = would_be_hours > max_hours if max_hours > 0 else False
        
        applications_with_hours.append({
            'application': application,
            'current_hours': current_hours,
            'max_hours': max_hours,
            'remaining_hours': remaining_hours,
            'hours_for_this': hours_for_this,
            'would_be_hours': would_be_hours,
            'would_exceed': would_exceed,
        })
    
    context = {
        'opportunity': opportunity,
        'applications_with_hours': applications_with_hours,
    }
    return render(request, 'opportunities/applications.html', context)


@login_required
@user_passes_test(is_org_admin)
def update_application_status(request, application_id, new_status):
    """Update application status."""
    application = get_object_or_404(Application, pk=application_id)
    
    # Check if user manages this opportunity's organisation
    if application.opportunity.organisation.admin != request.user:
        messages.error(request, 'You do not have permission to update this application.')
        return redirect('opportunities:list')
    
    if new_status not in dict(Application.STATUS_CHOICES):
        messages.error(request, 'Invalid status.')
        return redirect('opportunities:applications', pk=application.opportunity.pk)
    
    old_status = application.status
    application.status = new_status
    application.save()
    
    # Create notification for volunteer
    Notification.objects.create(
        user=application.volunteer,
        message=f'Your application for "{application.opportunity.title}" has been {new_status.lower()}.',
        type='OPPORTUNITY_UPDATE'
    )
    
    messages.success(request, f'Application status updated to {new_status}.')
    return redirect('opportunities:applications', pk=application.opportunity.pk)

