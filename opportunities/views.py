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
    if request.user.is_authenticated:
        try:
            user_application = Application.objects.get(
                volunteer=request.user,
                opportunity=opportunity
            )
        except Application.DoesNotExist:
            pass
    
    context = {
        'opportunity': opportunity,
        'user_application': user_application,
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
    
    applications = Application.objects.filter(opportunity=opportunity).order_by('-created_at')
    
    context = {
        'opportunity': opportunity,
        'applications': applications,
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

