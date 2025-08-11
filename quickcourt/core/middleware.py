from firebase_admin import auth as firebase_auth
from django.http import JsonResponse

class FirebaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            token = auth_header.replace("Bearer ", "")
            try:
                decoded_token = firebase_auth.verify_id_token(token)
                request.user_uid = decoded_token.get("uid")
                request.user_email = decoded_token.get("email")
            except Exception as e:
                return JsonResponse({"error": "Invalid token", "details": str(e)}, status=401)
        else:
            request.user_uid = None
        return self.get_response(request)
