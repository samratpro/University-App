from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.utils import timezone

''' gettext_lazy Means if application is translated into different languages, 
    this string will be translated accordingly. ''' 


class Logo(models.Model):
    logo_img = models.ImageField(upload_to='images/')
    icon_img = models.ImageField(upload_to='images/')
    
    def __str__(self):
        return 'Logo'
    

class Department(models.Model):
    department_name = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.department_name


class Semester(models.Model):
    semester_name = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.semester_name



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)       # is_active False for Email Verification 
        user = self.model(email=email, **extra_fields)    # Instead of username, here we used email pass none here
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        return self.create_user(email, password, **extra_fields)



class AppUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  
    activation_code = models.CharField(max_length=50, blank=True, null=True)
    password_reset_code = models.CharField(max_length=50, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, blank=True, null=True)
    admission_year =  models.CharField(default="2023", max_length=4, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)


    objects = UserManager()

    def activate(self):
        self.is_active = True
        self.activation_code = ''
        self.save()
    
    def save(self, *args, **kwargs):        # For email Lowercase
        if self.email:
            self.email.lower()
        super(AppUser, self).save(*args, **kwargs)
