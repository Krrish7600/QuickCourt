# admin_panel/views.py

from django.http import HttpResponse
from users.decorators import role_required


@role_required(['ADMIN'])
def admin_home(request):
    """Admin dashboard home page."""
    return HttpResponse("Admin Dashboard")
