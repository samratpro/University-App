from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
# Create your views here.





def login(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            remember_me = request.POST.get('remember_me')
            # user = authenticate(username=username, password=password)
            user = authenticate(request, email=email, password=password)
            print(user)
            if user is not None:
                auth.login(request, user)
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 14)   # Set a longer session timeout (e.g., 2 weeks)
                else:
                    request.session.set_expiry(0)    
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('profile')
            else:
                messages.info(request, 'Invalid password or username')
                return redirect(request.get_full_path()) # Need to return current URL cause next URL and normal URL are different
        else:
            template = 'user/login.html'
            return render(request, template)
    




def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        if password1 and password1 == password2:
            if AppUser.objects.filter(email=email):
                messages.info(request,"This email has already taken")
                return redirect('register')  
            else:
                user = AppUser.objects.create_user(is_active=False, email=email, password=password1, first_name=first_name, last_name=last_name)
                user.save()
                
                
                activation_code = get_random_string(30)
                user.activation_code = activation_code
                user.save()

                # Send activation email
                current_site = get_current_site(request)
                domain = current_site.domain
                from_email = 'noreply@mydomain.com'
                activation_link = f'{domain}/activate/{activation_code}/'
                send_mail(
                    'Activate Your Account',
                    f'Thank you for Registration, Following link to activate your account: {activation_link} \n Please don\'t share this link with any other',
                    from_email,
                    [email],
                    fail_silently=False
                )
                
                messages.info(request, 'Successfully created account')
                return redirect('login')
        else:
            messages.info(request, "Password dosen't match")
            return redirect('register')
    else:
        template = 'user/register/register.html'
        return render(request, template)
    
    
    
def activate_account(request, activation_code):
    try:
        user = AppUser.objects.get(activation_code=activation_code, is_active=False)
    except AppUser.DoesNotExist:
        return render(request, 'user/register/activation_failed.html')
    user.activate()   # This activate() method come from AppUser class of the models.py
    return render(request, 'user/register/activation_success.html')
    
    
    




def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = AppUser.objects.filter(email=email).first()

        if user:
            # Generate a password reset token and send it to the user via email
            forget_code = get_random_string(30)
            user.password_reset_code = forget_code
            user.save()
            
            protocol = 'https' if request.is_secure() else 'http'
            current_site = get_current_site(request)
            reset_url = f"{protocol}://{current_site.domain}/forget_password/confirm/{forget_code}/"
            subject = "Password Reset Request"
            message = f"Hello {user.first_name},\n\n"
            message += f"Click the following link to reset your password: {reset_url}"

            send_mail(subject, message, 'noreply@mydomain.com', [email], fail_silently=False)
            messages.success(request, 'We have sent you an email with instructions on how to reset your password.')
            return render(request, 'user/forget_password/send_code.html')
        else:
            messages.error(request, "This email doesn't exist")
            return render(request, 'user/forget_password/send_code.html')
    else:
        return render(request, 'user/forget_password/send_code.html')




def forget_password_confirm(request, forget_code):
    try:
        user = AppUser.objects.get(password_reset_code=forget_code)
        if user is not None:
            if request.method == 'POST':
                new_password1 = request.POST.get('new_password1')
                new_password2 = request.POST.get('new_password2')
                if new_password1 and new_password1 == new_password2:
                    user.password_reset_code = ''
                    user.set_password(new_password1)
                    user.save()
                    return render(request, 'user/forget_password/password_reset_done.html')
                else:
                    messages.error(request, "Password Dosen't Match")
                    return render(request, 'user/forget_password/set_new_password.html')
            else:
                return render(request, 'user/forget_password/set_new_password.html')
        else:
            messages.error(request, 'The password reset link is invalid or has expired.')
            return redirect('forget_password')
    except:
        return render(request, 'user/forget_password/password_reset_failed.html')


def logout(request):
    auth.logout(request)
    return redirect('login')



@login_required(login_url='login/')
def profile(request):
    user_profile = AppUser.objects.get(email=request.user.email)
    all_department = Department.objects.all()
    all_semseter = Semester.objects.all()
    context = {'user_profile': user_profile, 'all_department': all_department, 'all_semseter': all_semseter}

    if request.method == 'POST':
        profile_image = request.FILES.get('img_upload')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        admission_year = request.POST.get('admission_year')
        department_id = request.POST.get('department')
        semester_id = request.POST.get('semester')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password')

        if department_id:
            department_instance = get_object_or_404(Department, id=department_id)
            user_profile.department = department_instance
            user_profile.save()

        if semester_id:
            semester_instance = get_object_or_404(Semester, id=semester_id)
            user_profile.semester = semester_instance
            user_profile.save()

        if admission_year:
            user_profile.admission_year = admission_year
            user_profile.save()

        if first_name:
            user_profile.first_name = first_name
            user_profile.save()

        if last_name:
            user_profile.last_name = last_name
            user_profile.save()

        if email:
            user_profile.email = email
            user_profile.save()

        if password1 is not None and password1 == password2:
            user_profile.set_password(password1)
            user_profile.save()

        if profile_image:
            user_profile.profile_image = profile_image
            user_profile.save()

        return redirect('profile')

    return render(request, 'user/profile/profile.html', context=context)

