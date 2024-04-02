from typing import ItemsView
from django.db import models
import re

from django.db.models.fields.related import ManyToManyField 
import bcrypt 

from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class UserManager(models.Manager):
    def Validate_Registration(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        
        if len(User.objects.filter(email=postData['email'])) > 0:
            errors['existingUser'] = 'User already registered with that username'
        if len(postData['first_name']) < 2:
            errors['first_name']='First Name should be atleast 2 characters'
        # if len(postData['last_name']) < 2:
        #     errors['last_name']='Last Name should be atleast 2 characters'
        if not EMAIL_REGEX.match(postData['email']):             
            errors['email'] = ("Invalid email address!")
        if len(postData['password']) < 4:
            errors['first_name']='Password should be atleast 8 characters'
        if postData['password'] != postData['cf_password']:
            errors['confirm_pw']='Password and confirm password must match'
        # Secret password validation
        # if postData['secret_password'] != 'password':
        #     errors['secret_password'] = 'Invalid secret password'

        return errors
    
    def Login_Validator(self, postData):
        errors = {}
        checkUser = User.objects.filter(email = postData['log_email'])
        if len(checkUser) < 1:
            errors['NoUser'] = 'Invalid Username and Password cobination'
        elif not bcrypt.checkpw(postData['log_password'].encode(), checkUser[0].password.encode()):
            errors['passwordNoMatch'] = 'Invalid user and password combination'
        return errors


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)

    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=[('manager', 'Manager'), ('employee', 'Employee'), ('head', 'Head'), ('executive', 'Executive')])
   
    # secret_password = models.CharField(max_length=255)

    objects = UserManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_head(cls):
        head = cls(
            first_name='siva',
            last_name='subramanian',
            email='siva@agilisium.com',
            password=bcrypt.hashpw('1234'.encode(), bcrypt.gensalt()).decode(),
            phone_number='1234567890',
            role='head'
        )
        head.save()
        return head

# python manage.py shell

# from myapp.models import User

# head = User.create_head()


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

class EventDate(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    votes = models.IntegerField(default=0)

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_date = models.ForeignKey(EventDate, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')