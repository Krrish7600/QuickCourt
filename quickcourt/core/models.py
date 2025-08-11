from django.db import models

# Create your models here.
from django.db import models

class UserProfile(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)  # 'user', 'facility_owner', 'admin'
    avatar_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.full_name

import random
import datetime
from django.contrib.auth.models import User

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # OTP expires in 5 minutes (300 seconds)
        return (datetime.datetime.now(datetime.timezone.utc) - self.created_at).total_seconds() > 300

    @staticmethod
    def generate_otp():
        # Generate a random 6 digit OTP code
        return f"{random.randint(100000, 999999)}"
    
    

class Venue(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)  # city or area
    rating = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='venues/', null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
