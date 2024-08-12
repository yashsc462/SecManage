from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile

def user_login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate using the email field, which acts as the username
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)

                # Redirect based on the user type
                if user.is_superuser:
                    return redirect('dashboard')

                try:
                    user_profile = UserProfile.objects.get(user=user)
                    if user_profile.user_type == 'company':
                        return redirect('company_dashboard')
                    elif user_profile.user_type == 'fo':
                        return redirect('fo_dashboard')
                except UserProfile.DoesNotExist:
                    messages.error(request, "User profile not found.")
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')



def logout(request):
    auth_logout(request)
    return redirect('login') 


def dashboard(request):
    return render(request, 'admin/dashboard.html')

def view_emp(request):
    return render(request, 'company/view_emp.html')


def company_dashboard(request):
    return render(request, 'company/company_dashboard.html')


def fo_dashboard(request):
    return render(request, 'FO/fo_dashboard.html')


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile

def add_company(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        contact = request.POST['contact']
        gst_or_emergency = request.POST['gst_or_emergency']

        user = User.objects.create_user(
            username=email,  # Use email as the username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        UserProfile.objects.create(
            user=user,
            user_type='company',
            contact=contact,
            gst_or_emergency=gst_or_emergency,
        )
        return redirect('dashboard')  # Redirect to login or wherever you need

    return render(request, 'admin/add_company.html')


def add_fo(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        contact = request.POST['contact']
        gst_or_emergency = request.POST['gst_or_emergency']

        user = User.objects.create_user(
            username=email,  # Use email as the username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        UserProfile.objects.create(
            user=user,
            user_type='fo',
            contact=contact,
            gst_or_emergency=gst_or_emergency,
        )
        return redirect('dashboard')  # Redirect to login or wherever you need

    return render(request, 'admin/add_fo.html')

def companyList(request):
    companies=UserProfile.objects.filter(user_type='company')

    return render(request,'admin/companyList.html', {'companies':companies})


