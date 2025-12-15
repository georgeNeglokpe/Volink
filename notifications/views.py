from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification


@login_required
def list_notifications(request):
    """List all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Separate read and unread
    unread = notifications.filter(read_at__isnull=True)
    read = notifications.filter(read_at__isnull=False)
    
    context = {
        'unread_notifications': unread,
        'read_notifications': read,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def mark_as_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications:list')


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, read_at__isnull=True).update(
        read_at=timezone.now()
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')


@login_required
def notification_count(request):
    """Get count of unread notifications (JSON endpoint for badge)."""
    count = Notification.objects.filter(user=request.user, read_at__isnull=True).count()
    return JsonResponse({'count': count})

