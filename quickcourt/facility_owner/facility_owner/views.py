# facility_owner/views.py

from django.http import HttpResponse
from users.decorators import role_required


@role_required(['OWNER'])
def owner_home(request):
    """Facility Owner dashboard home page."""
    return HttpResponse("Facility Owner Dashboard")
