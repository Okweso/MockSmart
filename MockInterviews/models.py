from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
import datetime

# Create your models here.

class UsersManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    

class Users(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    profession = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =[]

    def __str__(self):
        return self.email

class MockVideos(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    video = models.FileField(upload_to='videos/')
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    feedback = models.TextField()
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)
    video_id = models.ForeignKey(MockVideos, on_delete=models.CASCADE, null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    clarity_score = models.FloatField(null=True, blank=True)
    body_language_score = models.FloatField(null=True, blank=True)
    avd_sentence_length = models.FloatField(null=True, blank=True)
    filler_word_count = models.IntegerField(null=True, blank=True)
    grammar_issues = models.TextField(null=True, blank=True)
    eye_contact = models.FloatField(null=True, blank=True)
    recommendations = models.TextField(null=True, blank=True)
    #date = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)

#careers@abnosoftwares.com / hr@abnosoftwares.com