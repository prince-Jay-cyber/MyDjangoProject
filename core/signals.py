from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from .models import Job, Profile

# Signal to create or update user profile when a User instance is created or updated
User = User  

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

@receiver(post_save, sender=Job)
def send_job_post_email(sender, instance, created, **kwargs):
    if not created:
        return  # only on brand‑new jobs

    print("✅ Job was created — sending emails now")   # debug line

    job_seekers = User.objects.filter(profile__role='job_seeker')
    recipient_list = [u.email for u in job_seekers if u.email]

    if recipient_list:
        subject  = f"New Job Posted: {instance.title}"
        message  = (
            f"A new job has been posted:\n\n"
            f"Title: {instance.title}\n"
            f"Location: {instance.location}\n\n"
            "Log in to apply!"
        )
        from_email = 'no-reply@yourdomain.com'
        data = [(subject, message, from_email, [email]) for email in recipient_list]
        send_mass_mail(data, fail_silently=True)