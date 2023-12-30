from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import *
# Create your views here.






@login_required
def submit_vote(request):
    user = request.user
    exist_vote = Vote.objects.filter(department=user.department, semester=user.semester).first()
    if exist_vote:
        has_voted_before = VoteRecord.objects.filter(student=user).exists()
        if not has_voted_before:
            if request.method == 'POST':
                voted_for_id = request.POST.get('voted_for')
                voted_for_user = get_object_or_404(AppUser, id=voted_for_id) 
                new_vote = VoteRecord(student=user, voted_for=voted_for_user, vote=exist_vote)
                new_vote.save()
                return redirect('vote_results')
            else:
                users = AppUser.objects.filter(semester=user.semester, department=user.department).all()
                return render(request, 'vote/submit_vote.html', {'users': users})
        else:
            return render(request, 'vote/voted_before.html', {'exist_vote':exist_vote})
    else:
        return render(request, 'vote/vote_not_open.html')
    


@login_required
def vote_results(request):
    user = request.user
    existing_vote = Vote.objects.filter(department=user.department, semester=user.semester).first()
    if existing_vote:
        if existing_vote.end_date <= timezone.now():
            # Annotate votes received by each student for a specific vote
            vote_records = (
                VoteRecord.objects
                .filter(vote=existing_vote)  # Filters VoteRecords by the given existing_vote
                .values(
                    'voted_for__id',          # Retrieves the ID of the student voted for
                    'voted_for__first_name',  # Retrieves the first name of the voted-for student
                    'voted_for__last_name',   # Retrieves the last name of the voted-for student
                    'voted_for__profile_image' # Retrieves the profile image of the voted-for student
                )
                .annotate(total_votes=Count('voted_for'))  # Counts the total votes received by each voted-for student
            )
            
            # Get all students in the department and semester
            all_students = AppUser.objects.filter(semester=user.semester, department=user.department)
            
            # Combine both vote records and students who haven't received votes
            # Adding 'total_votes' to all students to indicate votes received
            for student in all_students:
                student.total_votes = next((record['total_votes'] for record in vote_records if record['voted_for__id'] == student.id), 0)
            '''
                1. `student.total_votes` for assigns a new attribute to each student object. 
                    It adds dynamically to the student object retrieved from all_students.

                2. student: Represents each student in the loop.

                3. record['total_votes'] for record in vote_records if record['voted_for__id'] == student.id: 
                   This part is a generator expression. 
                   It iterates through vote_records and filters to find records where the voted_for user ID matches 
                   the current student.id. It retrieves the total_votes for that student if such a record is found.

                4. filters the vote_records queryset to find the records where the voted_for 
                   user ID matches the current student.id. It retrieves the total_votes for that student if found.

                5. next(): This function retrieves the next value from the generator expression. 

                6. If no matching record is found (i.e., the student hasn't received any votes), it returns a default value of 0.
            '''     
            return render(request, 'vote/vote_results.html', {'all_students': all_students})
        else:
            return render(request, 'vote/vote_running.html', {'existing_vote': existing_vote})
    else:
        return render(request, 'vote/no_vote_results.html')