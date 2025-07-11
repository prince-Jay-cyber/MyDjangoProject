from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Job(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='jobs_posted')

    def get_company_display_name(self):
        if self.posted_by:
            try:
                profile = self.posted_by.profile
                if profile.role == 'employer' and profile.company_name:
                    return profile.company_name
                elif self.posted_by.is_superuser:
                    return "System Admin"
            except Exception:
                pass
        return "Unknown Poster"





    
    def __str__(self):
        return self.title

class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)

class JobCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Font Awesome class, e.g., 'fas fa-code'")
    color = models.CharField(max_length=20, help_text="Bootstrap text color class, e.g., 'text-primary'")
    job_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Job Categories'

    def __str__(self):
        return self.name
     
class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    email_sent_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"

class Profile(models.Model):
    ROLE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    is_employer = models.BooleanField(default=False)

    # Common fields
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    # Job Seeker fields
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)

    # Employer fields
    company_name = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    last_job_view = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.job.title}"
    

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.user.username if self.user else 'Anonymous'}"


class JobAlert(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert: {self.subject} @ {self.sent_at.strftime('%Y-%m-%d %H:%M')}"