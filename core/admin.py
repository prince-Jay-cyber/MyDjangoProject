from django.contrib import admin
from .models import Application, Job
from django.utils.html import format_html
from .models import JobCategory
from .models import BlogPost
from .models import Testimonial
from django.core.mail import send_mass_mail
from .models import JobAlert
# from .models import User
from django.contrib import messages
from django.contrib.auth.models import User


admin.site.site_header = "NsaJob Admin"
admin.site.site_title = "NsaJob Admin"
admin.site.index_title = "Welcome to the Admin Dashboard"


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0


class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'created_at']
    inlines = [ApplicationInline]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'applied_at', 'status', 'resume_link')
    list_filter = ('status', 'applied_at')

    def resume_link(self, obj):
        if obj.cv:
            return format_html("<a href='{}' target='_blank'>Download</a>", obj.cv.url)
        return "No file"
    resume_link.short_description = 'Resume'

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_count', 'color')
    search_fields = ('name',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title', 'summary']
    ordering = ['-created_at']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    actions = ['approve_selected']

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
    approve_selected.short_description = "Approve selected testimonials"


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent_at')
    readonly_fields = ('sent_at',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:  # Only send on creation
            job_seekers = User.objects.filter(profile__role='job_seeker')
            recipient_list = [user.email for user in job_seekers if user.email]

            messages_data = [
                (obj.subject, obj.message, 'no-reply@yourdomain.com', [email])
                for email in recipient_list
            ]
            send_mass_mail(messages_data, fail_silently=False)

            messages.success(request, f"Job alert sent to {len(recipient_list)} job seekers.")


admin.site.register(Job, JobAdmin)
# admin.site.register(Application)
