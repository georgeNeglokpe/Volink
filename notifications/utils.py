"""
Utility functions for notifications.
Wizard-of-oz: Email notifications are simulated.
"""
import logging

logger = logging.getLogger(__name__)


def send_email_notification(user, message, subject="Volink Notification"):
    """
    Simulate sending an email notification.
    In production, this would send an actual email.
    For now, we log it instead.
    
    Args:
        user: User instance
        message: Email message body
        subject: Email subject
    """
    # Log the email instead of sending
    logger.info(f"[SIMULATED EMAIL] To: {user.email}, Subject: {subject}, Message: {message}")
    
    # In production, you would use Django's email backend:
    # from django.core.mail import send_mail
    # send_mail(
    #     subject=subject,
    #     message=message,
    #     from_email='noreply@volink.com',
    #     recipient_list=[user.email],
    #     fail_silently=False,
    # )

