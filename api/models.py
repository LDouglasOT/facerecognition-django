import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime

from user.models import Parent


class tempOtp(models.Model):
    phone = models.CharField(max_length=10)
    otp = models.CharField(max_length=6)
    timestamp = models.TimeField(auto_now_add=True,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def has_ten_minutes_passed(self):
        if self.timestamp:
            current_time = timezone.now().time()       
            timestamp_datetime = timezone.make_aware(datetime.combine(timezone.now().date(), self.timestamp))
    
            return current_time >= (timestamp_datetime + timedelta(minutes=10)).time()
        return False
    def __str__(self):
        return self.phone
    

class ClearenceCode(models.Model):
    code = models.CharField(max_length=10)
    created_by = models.ForeignKey(Parent, on_delete=models.CASCADE,blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateField(auto_now_add=True,blank= True, null=True)
    time_created = models.TimeField(auto_now_add=True,blank=True, null=True)
    visitor_name = models.CharField(max_length=100,blank=True)
    visitor_contact = models.CharField(max_length=100, blank=True)
    visitor_relationship = models.CharField(max_length=100,blank=True)
    date_created = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    studentone = models.CharField(max_length=100, blank=True)
    studenttwo = models.CharField(max_length=100, blank=True)
    studentthree = models.CharField(max_length=100, blank=True) 
    studentfour = models.CharField(max_length=100, blank=True)
    studentfive = models.CharField(max_length=100, blank=True)
    studentsix = models.CharField(max_length=100, blank=True)
    studentseven = models.CharField(max_length=100, blank=True)
    reason = models.CharField(max_length=100, blank=True)
    pid = models.UUIDField(default=uuid.uuid4, editable=False)
    expiry_date = models.DateField(blank=True, null=True)
    trmpvisiting = models.CharField(max_length=1000,blank=True)
    def __str__(self):
        return self.code

class Notifications(models.Model):
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
    
# models.py
from django.db import models

class Receipt(models.Model):
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True, default="None")
    contact = models.CharField(max_length=255, blank=True, null=True, default="None")
    students = models.CharField(max_length=255, blank=True, null=True, default="None")

    def __str__(self):
        return f"{self.reason} - {self.timestamp}"


