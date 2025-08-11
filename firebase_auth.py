import firebase_admin
from firebase_admin import auth as firebase_auth
from django.http import JsonResponse

class FirebaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        id_token = request.META.get('HTTP_AUTHORIZATION')
        if id_token:
            id_token = id_token.replace("Bearer ", "")
            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
                request.user_uid = decoded_token["uid"]
                request.user_email = decoded_token.get("email")
            except Exception as e:
                return JsonResponse({"error": "Invalid token", "details": str(e)}, status=401)
        else:
            request.user_uid = None
        return self.get_response(request)
