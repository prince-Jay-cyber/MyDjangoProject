from django.utils import timezone
from .models import Job

def new_job_count(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'profile'):
        return {'new_job_count': 0}

    last_seen = request.user.profile.last_job_view
    count = Job.objects.filter(created_at__gt=last_seen).count()
    return {'new_job_count': count}
