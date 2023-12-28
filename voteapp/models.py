from django.db import models
from django.utils import timezone
from userapp.models import *
# Create your models here.


class Vote(models.Model):
    vote_name = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    deparment = models.ForeignKey(Deperment, on_delete=models.SET_NULL, blank=True, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, blank=True, null=True)
    vote_by = models.ForeignKey(AppUser, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.vote_name