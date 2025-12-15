from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully for {user.username}!')
            login(request, user)
            return redirect('accounts:profile_redirect')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view."""
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='accounts/login.html')(request)


@login_required
def profile_redirect(request):
    """Redirect users to appropriate dashboard based on role."""
    if request.user.is_volunteer():
        return redirect('volunteers:dashboard')
    elif request.user.is_org_admin():
        return redirect('organisations:dashboard')
    elif request.user.is_staff_admin():
        return redirect('admin:index')
    return redirect('landing')

