from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .models import OTP
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from .models import Venue 

# Create your views here.
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_auth(request):
    if request.user_uid:
        return JsonResponse({"message": "Hello, " + request.user_email})
    return JsonResponse({"error": "Unauthorized"}, status=401)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .firebase_config import db
from firebase_admin import firestore
import json
from datetime import datetime

# ----- Helper -----
def doc_to_dict(doc):
    d = doc.to_dict()
    d['id'] = doc.id
    return d

# ----- Venues: list (public) -----
def list_venues(request):
    try:
        # only approved venues shown; if you don't have approved flag remove where
        q = db.collection('venues').where('approved', '==', True).stream()
        venues = [doc_to_dict(d) for d in q]
        return JsonResponse({'venues': venues})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ----- Single venue -----
def single_venue(request, venue_id):
    try:
        doc = db.collection('venues').document(venue_id).get()
        if not doc.exists:
            return JsonResponse({'error': 'Venue not found'}, status=404)
        return JsonResponse(doc_to_dict(doc))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ----- Create booking (transactional to avoid double-booking) -----
@csrf_exempt
def create_booking(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not getattr(request, 'user_uid', None):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required = ['venue_id', 'court_id', 'date', 'time_slot', 'price']
    if not all(k in data for k in required):
        return JsonResponse({'error': 'Missing fields; required: ' + ','.join(required)}, status=400)

    venue_id = data['venue_id']
    court_id = data['court_id']
    date = data['date']           # e.g. '2025-08-25'
    time_slot = data['time_slot'] # e.g. '18:00-19:00'
    price = data['price']

    bookings_ref = db.collection('bookings')

    @firestore.transactional
    def txn_create(tx):
        # check conflict
        q = bookings_ref \
            .where('court_id', '==', court_id) \
            .where('date', '==', date) \
            .where('time_slot', '==', time_slot) \
            .limit(1)
        existing = q.get(transaction=tx)
        if existing:
            raise ValueError('Slot already booked')
        new_ref = bookings_ref.document()
        booking_doc = {
            'user_uid': request.user_uid,
            'venue_id': venue_id,
            'court_id': court_id,
            'date': date,
            'time_slot': time_slot,
            'price': price,
            'status': 'confirmed',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        tx.set(new_ref, booking_doc)
        return new_ref.id

    transaction = db.transaction()
    try:
        booking_id = txn_create(transaction)
        return JsonResponse({'message': 'Booking created', 'booking_id': booking_id})
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=409)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ----- List current user's bookings -----
def my_bookings(request):
    if not getattr(request, 'user_uid', None):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        q = db.collection('bookings') \
            .where('user_uid', '==', request.user_uid) \
            .order_by('created_at', direction=firestore.Query.DESCENDING) \
            .stream()
        bookings = [doc_to_dict(d) for d in q]
        return JsonResponse({'bookings': bookings})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ----- Cancel a booking (only owner of booking) -----
@csrf_exempt
def cancel_booking(request, booking_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not getattr(request, 'user_uid', None):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        ref = db.collection('bookings').document(booking_id)
        snap = ref.get()
        if not snap.exists:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        data = snap.to_dict()
        if data.get('user_uid') != request.user_uid:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        ref.update({'status': 'cancelled'})
        return JsonResponse({'message': 'Booking cancelled'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def landingpage(request):
    return render(request, "landingpage.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            # Credentials are valid, generate OTP
            code = OTP.generate_otp()
            OTP.objects.create(user=user, code=code)
            send_mail(
    'Your OTP Code',
    f'Your OTP code is: {code}',
    'your_email@example.com',  # Replace with your "from" email
    [user.email],  # The user's email address
    fail_silently=False,
)
        

            # TODO: send OTP to user via email or SMS
            print(f"OTP for {user.username}: {code}")  # For testing purpose

            # Store user id in session for OTP verification step
            request.session['user_id_for_otp'] = user.id

            # Redirect to OTP verification page
            return redirect('api:otp')
        else:
            # Invalid credentials, reload login with error
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, 'signup.html')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            login(request, user)  # Logs the user in immediately after signup
            return redirect('landingpage')  # Or redirect to login or dashboard
    return render(request, 'signup.html')

def otp_verify(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id_for_otp')
        otp_entered = request.POST.get('otp')

        if not user_id:
            # No user id saved in session, redirect to login
            return redirect('login')

        try:
            user = User.objects.get(id=user_id)
            otp_obj = OTP.objects.filter(user=user).last()  # Get latest OTP
        except User.DoesNotExist:
            return redirect('login')

        # Check if OTP matches and is not expired
        if otp_obj and otp_obj.code == otp_entered and not otp_obj.is_expired():
            # OTP valid - log the user in
            login(request, user)

            # Clean session
            del request.session['user_id_for_otp']

            # Redirect to home/dashboard
            return redirect('home')
        else:
            return render(request, 'otp.html', {'error': 'Invalid or expired OTP'})

    else:
        return render(request, 'otp.html')
    
def home_view(request):
    return render(request, 'home.html')

def otp_view(request):
    email = request.GET.get('email', '')  # get email from query string if passed
    context = {'email': email}
    return render(request, 'otp.html', context)

def search_venues(request):
    query = request.GET.get('q', '')
    if query:
        venues = Venue.objects.filter(location__icontains=query)[:10]  # filter by location contains query, limit 10 results
        results = [{
            'id': v.id,
            'name': v.name,
            'location': v.location,
            'rating': v.rating,
            'tags': [tag.name for tag in v.tags.all()] if hasattr(v, 'tags') else [],
            'image_url': v.image.url if v.image else ''
        } for v in venues]
    else:
        results = []

    return JsonResponse({'venues': results})

from django.shortcuts import render
from .models import Venue

def home_view(request):
    query = request.GET.get('location', '')  # get 'location' param from URL
    if query:
        venues = Venue.objects.filter(location__icontains=query)
    else:
        venues = Venue.objects.all()
    context = {
        'venues': venues,
        'search_location': query,
    }
    return render(request, 'home.html', context)

# views.py
from django.shortcuts import render
from .models import Venue

def home(request):
    search_location = request.GET.get('location', '').strip()
    
    if search_location:
        venues = Venue.objects.filter(location__icontains=search_location)
    else:
        venues = Venue.objects.all()
    
    context = {
        'venues': venues,
        'search_location': search_location,
    }
    return render(request, 'home.html', context)

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')

