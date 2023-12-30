from django.db import models
from django.utils import timezone
from userapp.models import *
# Create your models here.


class Vote(models.Model):
    vote_name = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, blank=True, null=True)
    vote_created_by = models.ForeignKey(AppUser, related_name='votes_given', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        vote_name = self.vote_name if self.vote_name else ""
        vote_created_by = self.vote_created_by if self.vote_created_by else ""
        return f"{vote_name} by {vote_created_by}"
    


class VoteRecord(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    student = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    voted_for = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='received_votes')
    voted_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('vote', 'student')  # Ensures each student can give one vote only
    
    def __str__(self):
        voted = self.student
        vote_for = self.voted_for
        return f"{voted.first_name} {voted.last_name} voted for {vote_for.first_name} {vote_for.last_name}"