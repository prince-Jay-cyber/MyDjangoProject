# core/urls.py
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from .views import jobseeker_settings




urlpatterns = [
    path('', views.landing, name='landing'),
    path('choose-login/', views.choose_login, name='choose_login'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='core/logout.html'), name='logout'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('jobseeker/settings/', jobseeker_settings, name='jobseeker_settings'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_for_job, name='apply_for_job'),
    path('jobs/<int:job_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('jobs/delete/<int:pk>/', views.delete_job, name='delete_job'),
    path('explore-jobs/', views.job_explore, name='job_explore'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('bookmarked/', views.bookmarked_jobs, name='bookmarked_jobs'),
    path('recommendations/', views.recommend_jobs, name='recommend_jobs'),
    path('employer/jobs/create/', views.create_job, name='create_job'),
    path('employer/jobs/<int:job_id>/update/', views.update_job, name='update_job'),
    path('employer/jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('employer/register/', views.employer_register, name='employer_register'),
    path('employer/login/', views.employer_login_view, name='employer_login'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/dashboard/main/', views.employer_dashboard_main, name='employer_dashboard_main'),
    path('employer/profile/', views.employer_profile, name='employer_profile'),
    path('employer/create-job/', views.create_job, name='create_job'),
    path('employer/my-jobs/', views.my_jobs, name='my_jobs'),
    path('employer/applicants/', views.view_applicants, name='view_applicants'),
    path('employer/applications/<int:application_id>/email/', views.send_email_to_applicant, name='send_email_to_applicant'),
    path('application/<int:app_id>/status/<str:new_status>/', views.update_application_status, name='update_application_status'),
    path('applications/delete/<int:app_id>/', views.delete_application, name='delete_application'),
    path('employer/settings/', views.employer_settings, name='employer_settings'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('interview-tips/', views.tips, name='tips'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('track-application/', views.track_application, name='track_application'),
    path('subscribe/', views.newsletter_signup, name='newsletter_signup'),
    path('career_tips/', views.career_tips, name='blog_list'),
    path('career_tips/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('download-cv/<int:application_id>/', views.download_cv, name='download_cv'),
    
   # Jobseeker password reset flow
    path('jobseeker/password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/auth/jobseeker/password_reset_form.html',
        email_template_name='core/auth/jobseeker/password_reset_email.html',
        subject_template_name='core/auth/jobseeker/password_reset_subject.txt',
        success_url='/jobseeker/password-reset/done/'
    ), name='jobseeker_password_reset'),

    path('jobseeker/password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/auth/jobseeker/password_reset_done.html'
    ), name='jobseeker_password_reset_done'),

    path('jobseeker/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/auth/jobseeker/password_reset_confirm.html'
    ), name='jobseeker_password_reset_confirm'),

    path('jobseeker/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/auth/jobseeker/password_reset_complete.html'
    ), name='jobseeker_password_reset_complete'),

    path('jobseeker/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Employer password reset flow
    path('employer/password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/auth/employer/password_reset_form.html',
        email_template_name='core/auth/employer/password_reset_email.html',
        subject_template_name='core/auth/employer/password_reset_subject.txt',
        success_url='/employer/password-reset/done/'
    ), name='employer_password_reset'),

    path('employer/password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/auth/employer/password_reset_done.html'
    ), name='employer_password_reset_done'),

    path('employer/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/auth/employer/password_reset_confirm.html'
    ), name='employer_password_reset_confirm'),

    path('employer/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/auth/employer/password_reset_complete.html'
    ), name='employer_password_reset_complete'),

] 
