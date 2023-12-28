from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import *
# Create your views here.






@login_required
def submit_vote(request):
    user = request.user
    exist_vote = Vote.objects.filter(deparment=user.deperment, semester=user.semester).exists()
    if exist_vote:
        has_voted_before = Vote.objects.filter(vote_by=user).exists()
        if not has_voted_before:
            if request.method == 'POST':
                user.vote.create(voted_by=user)
                return redirect('vote-results')
            else:
                return render(request, 'vote/submit_vote.html')
        else:
            return render(request, 'vote/voted_before.html')
    else:
        return render(request, 'vote/vote_not_open.html')




@login_required
def vote_results(request):
    user = request.user
    existing_vote = Vote.objects.filter(deparment=user.deperment, semester=user.semester).first()
    if existing_vote:
        if existing_vote.end_date <= timezone.now():
            return render(request, 'vote/vote_results.html', {'existing_vote': existing_vote})
        else:
            return render(request, 'vote/vote_running.html', {'existing_vote': existing_vote})
    else:
        return render(request, 'vote/no_vote_results.html')
