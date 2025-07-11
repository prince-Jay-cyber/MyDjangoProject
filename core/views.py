# core/views.py
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import SubscriberForm
from django.conf import settings
from .forms import RegisterForm 
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.template.loader import render_to_string
from core.models import Job, Application  
from .models import Application
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import EmployerSettingsForm
from .forms import UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm
from .forms import LoginForm
from .models import JobCategory
from .models import BlogPost
from .models import Testimonial
from django.utils import timezone
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.http import Http404, FileResponse
import os
from django.shortcuts import get_object_or_404
from .models import Application
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt




try:
    import dialogflow_v2 as dialogflow
except ImportError:
    dialogflow = None  # To avoid runtime errors if dialogflow is not installed


from .models import Job, Bookmark, Application, Profile
from .forms import (
    RegisterForm,
    LoginForm,
    JobForm,
    ContactForm,
    ApplicationForm,
    JobFilterForm,
    ProfileForm,
)
def is_employer(user):
    return hasattr(user, 'profile') and user.profile.role == 'employer'

def choose_login(request):
    return render(request, 'core/choose_login.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile as job seeker
            Profile.objects.create(user=user, role='job_seeker')
            login(request, user)
            messages.success(request, "You have been signed up successfully!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form, 'hide_nav': True})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get("remember_me")
            user = authenticate(request, username=username, password=password)
            
            if user is not None:

                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close
                else:
                    request.session.set_expiry(1209600) 

                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html',{'form': form, 'hide_nav': True})


def newsletter_signup(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save()
            # Notify admin
            send_mail(
                'New Newsletter Subscriber',
                f'Email: {subscriber.email}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'You have successfully subscribed!')
        else:
            if Subscriber.objects.filter(email=form.data.get('email')).exists():
                messages.warning(request, 'This email is already subscribed.')
            else:
                messages.error(request, 'Please enter a valid email address.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def home(request):
    stats = {
        'jobs_count': Job.objects.count(),
        'employers_count': User.objects.filter(profile__is_employer=True).count(),
        'applications_count': Application.objects.count(),
        'users_count': User.objects.filter(is_active=True).count(),
    }

    form = JobFilterForm(request.GET)
    jobs = Job.objects.all()
    categories = JobCategory.objects.all()

    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')

        if keyword:
            jobs = jobs.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
        if location:
            jobs = jobs.filter(location__icontains=location)
        if category:
            jobs = jobs.filter(category__icontains=category)

    # Suggested jobs (excluding those posted by the current user)
    suggested_jobs = []
    if request.user.is_authenticated:
        job_pool = list(Job.objects.exclude(posted_by=request.user))
        random.shuffle(job_pool)
        suggested_jobs = job_pool[:3]
    else:
        job_pool = list(jobs)
        random.shuffle(job_pool)
        suggested_jobs = job_pool[:3]

    jobs = jobs.order_by('-created_at')

    return render(request, 'core/home.html', {
        'jobs': jobs,
        'form': form,
        'categories': categories,
        'hide_nav': True,
        'stats': stats,
        'suggested_jobs': suggested_jobs,
    })


@csrf_exempt
def delete_application(request, app_id):
    if request.method == "POST":
        application = get_object_or_404(Application, id=app_id, user=request.user)
        application.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def profile(request):
    return render(request, 'core/profile.html')

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'core/job_detail.html', {'job': job})



@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user  # ✅ correct field name
            application.save()


            # ✅ Send confirmation email
            send_mail(
                subject='Job Application Confirmation',
                message=f"Hi {request.user.username},\n\nYou successfully applied for: {job.title}\n\nLocation: {job.location}",
                from_email=None,  # uses DEFAULT_FROM_EMAIL
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            messages.success(request, "Application submitted successfully!")
            return redirect('my_applications')

    else:
        form = ApplicationForm()

    return render(request, 'core/apply.html', {'form': form, 'job': job})


@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'core/my_applications.html', {'applications': applications})

@login_required
def view_applicants(request):
    applications = Application.objects.filter(job__employer=request.user).order_by('-applied_at')
    paginator = Paginator(applications, 2)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employer/applicants.html', {
        'applications': page_obj
    })

@login_required
def update_application_status(request, app_id, new_status):
    application = get_object_or_404(Application, id=app_id)

    # Optional: Ensure only employers can do this
    if request.user != application.job.employer:
        return redirect('unauthorized')  # or raise PermissionDenied

    application.status = new_status
    application.save()
    return redirect('view_applicants')


@login_required
def employer_settings(request):
    user = request.user
    profile = user.profile
    settings_form = EmployerSettingsForm(request.POST or None, request.FILES or None, instance=profile)
    password_form = PasswordChangeForm(user, request.POST or None)

    if request.method == 'POST':
        if 'save_settings' in request.POST and settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Settings updated successfully.')
            return redirect('employer_settings')
        
        if 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('employer_settings')
        else:
            messages.error(request, 'Please correct the error below.')

    return render(request, 'employer/settings.html', {
        'settings_form': settings_form,
        'password_form': password_form,
    })


@login_required
def view_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    application_count = Application.objects.filter(applicant=request.user).count()
    context = {
        'user': request.user,
        'profile': profile,
        'application_count': application_count
    }
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    # Automatically create profile if it doesn't exist
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('view_profile')
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def jobseeker_settings(request):
    if request.method == 'POST':
        if 'save_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            password_form = CustomPasswordChangeForm(request.user)  # empty form

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('jobseeker_settings')

        elif 'change_password' in request.POST:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileUpdateForm(instance=request.user.profile)
            password_form = CustomPasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Password changed successfully.")
                return redirect('jobseeker_settings')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'core/jobseeker_settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    })


def job_list(request):
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        request.user.profile.last_job_view = timezone.now()
        request.user.profile.save(update_fields=["last_job_view"])

    form = JobFilterForm(request.GET)
    jobs = Job.objects.all()

    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')

        if keyword:
            jobs = jobs.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
        if location:
            jobs = jobs.filter(location__icontains=location)
        if category:
            jobs = jobs.filter(category__icontains=category)

    jobs = jobs.order_by('-created_at')
    paginator = Paginator(jobs, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/job_list.html', {
        'form': form,
        'jobs': page_obj,   
        'page_obj': page_obj,
    })

def job_explore(request):
    all_jobs = Job.objects.order_by('-created_at')
    paginator = Paginator(all_jobs, 5)  # Adjust per page if needed

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/job_explore.html', {
        'jobs': page_obj,
        'page_obj': page_obj
    })



def landing(request):
    categories = JobCategory.objects.all()
    posts = BlogPost.objects.order_by('-created_at')[:3]
    latest_jobs = Job.objects.order_by('-created_at')[:3]
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')[:3]  # Get latest 3 approved testimonials
    return render(request, 'core/landing.html', {'latest_jobs': latest_jobs, 'categories': categories, 'posts': posts, 'testimonials': testimonials})

def get_new_job_count(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        last_seen = request.user.profile.last_job_view
        new_jobs = Job.objects.filter(posted_at__gt=last_seen).count()
        return {'new_job_count': new_jobs}
    return {'new_job_count': 0}

@login_required
def toggle_bookmark(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, job=job)
    if not created:
        bookmark.delete()
        messages.success(request, "Job removed from bookmarks.")
    else:
        messages.success(request, "Job bookmarked successfully.")
    return redirect('job_detail', job_id=job_id)

@login_required
def bookmarked_jobs(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, 'core/bookmarked_jobs.html', {'bookmarks': bookmarks, 'hide_footer': True})

@login_required
def recommend_jobs(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Get categories of jobs the user has applied for
    applied_categories = Application.objects.filter(applicant=user).values_list('job__category', flat=True).distinct()
    
    # Get the user's location from their profile
    user_location = profile.phone  # Assuming phone field stores location for now
    
    # Recommend jobs based on applied categories and location
    recommended_jobs = Job.objects.none()
    if applied_categories:
        recommended_jobs = recommended_jobs | Job.objects.filter(category__in=applied_categories)
    if user_location:
        recommended_jobs = recommended_jobs | Job.objects.filter(location__icontains=user_location)
        
    # Exclude jobs the user has already applied for
    applied_jobs = Application.objects.filter(applicant=user).values_list('job__id', flat=True)
    recommended_jobs = recommended_jobs.exclude(id__in=applied_jobs).distinct()
    
    return render(request, 'core/recommended_jobs.html', {'jobs': recommended_jobs})

def employer_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile as employer
            Profile.objects.create(user=user, role='employer')
            login(request, user)
            return redirect('employer_dashboard')
    else:
        form = RegisterForm()
    return render(request, 'core/employer_register.html', {'form': form, 'hide_nav': True})


def employer_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = request.POST.get('remember_me')
            user = authenticate(request, username=username, password=password)
            if user and hasattr(user, 'profile') and user.profile.role == 'employer':

                if not remember_me:
                    request.session.set_expiry(0)  # Expires on browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks (in seconds)


                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('employer_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'core/employer_login.html', {'form': form, 'hide_nav': True})


@login_required(login_url='employer_login')
@user_passes_test(is_employer, login_url='employer_login')
def employer_dashboard(request):
    jobs = Job.objects.filter(employer=request.user)
    applications = Application.objects.filter(job__employer=request.user)

    my_jobs_count = Job.objects.filter(employer=request.user).count()
    applicants_count = Application.objects.filter(job__employer=request.user).count()
    email_sent_total = Application.objects.filter(job__employer=request.user).aggregate(total=Sum('email_sent_count'))['total'] or 0

    context = {
        'my_jobs_count': my_jobs_count,
        'applicants_count': applicants_count,
        'jobs_count': jobs.count(),
        'applications_count': applications.count(),
        'email_sent_total': email_sent_total,
        'jobs': jobs.order_by('-created_at')[:5],
        'applications': applications.order_by('-applied_at')[:5],
    }
    return render(request, 'employer/dashboard.html', {**context, 'hide_nav': True})


@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    job.delete()
    return redirect('my_jobs')

def employer_dashboard_main(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('employer/dashboard_main.html', {}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'employer/dashboard_main.html', {'hide_nav': True})


def send_email_to_applicant(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_body = request.POST.get('message')

        employer = request.user
        company_email = employer.email  # Customize if needed

        full_message = f"""
        Message from: {employer.get_full_name()} ({company_email})

        {message_body}
        """

        email = EmailMessage(
            subject=subject,
            body=full_message,
            from_email=settings.EMAIL_HOST_USER,  # System email
            to=[application.applicant.email],
            reply_to=[company_email],  # 👈 This line makes replies go to employer
        )
        email.send()

        # Track email count (optional, requires model update)
        application.email_sent_count += 1
        application.save()

        messages.success(request, "Email sent successfully to the applicant.")
        return redirect('employer_dashboard')

    return render(request, 'employer/send_email.html', {'application': application})


@login_required
def employer_profile(request):
    return render(request, 'employer/employer_profile.html')


def download_cv(request, application_id):
    application = get_object_or_404(Application, pk=application_id)

    # Optional permission check
    if request.user != application.job.employer:
        return HttpResponseForbidden("You're not authorized to download this CV.")

    if not application.cv:
        raise Http404("CV not found.")

    try:
        return FileResponse(
            application.cv.open('rb'),
            as_attachment=True,
            filename=os.path.basename(application.cv.name)
        )
    except FileNotFoundError:
        raise Http404("File not found on the server.")


@login_required
def create_job(request):
    if request.user.profile.role != 'employer':
        return redirect('home')

    form = JobForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        job.employer = request.user
        job.posted_by = request.user 
        job.save()
        messages.success(request, 'Job posted successfully.')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('employer/partials/create_job_partial.html', {'form': JobForm()}, request=request)
            return JsonResponse({'success': True, 'html': html})
        else:
            return redirect('employer_dashboard')

    # For AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('employer/partials/create_job_partial.html', {'form': form}, request=request)
        return JsonResponse({'html': html})

    # Regular full page (fallback)
    return render(request, 'employer/create_job.html', {'form': form})

@login_required
def my_jobs(request):
    # Ensure only employers can access
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'employer':
        return redirect('my_jobs')

    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')

    # AJAX support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # You need to create 'employer/partials/my_jobs_partial.html'
        html = render_to_string('employer/partials/my_jobs_partial.html', {'jobs': jobs}, request=request)
        return JsonResponse({'html': html})

    return render(request, 'employer/my_jobs.html', {'jobs': jobs})


@login_required
def update_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, created_by=request.user)
    if request.user.profile.role != 'employer':
        return redirect('home')
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('employer_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'core/job_form.html', {'form': form})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, created_by=request.user)
    if request.user.profile.role != 'employer':
        return redirect('home')
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully.')
        return redirect('employer_dashboard')
    return render(request, 'core/job_confirm_delete.html', {'job': job})

def about(request):
    return render(request, 'core/about.html')

def faq(request):
    return render(request, 'core/faq.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Send email or save to database
            messages.success(request, 'Your message has been sent successfully.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    total_users = User.objects.count()
    total_jobs = Job.objects.count()
    total_applications = Application.objects.count()

    jobs_per_category = Job.objects.values('category').annotate(count=Count('category'))

    context = {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'jobs_per_category': jobs_per_category,
    }
    return render(request, 'core/admin_dashboard.html', context)

def resume_builder(request):
    return render(request, 'core/resume_builder.html')

def tips(request):
    return render(request, 'core/tips.html')

def saved_jobs(request):
    return render(request, 'core/saved_jobs.html')

def track_application(request):
    return render(request, 'core/track_application.html')

def career_tips(request):
    posts = BlogPost.objects.order_by('-created_at')[:3]  # Show latest 3
    return render(request, 'core/career_tips.html', {'posts': posts})

def blog_detail(request, post_id):
    post = BlogPost.objects.get(id=post_id)
    return render(request, 'core/blog_detail.html', {'post': post})




