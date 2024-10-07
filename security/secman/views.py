from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile
from datetime import datetime, timedelta, time
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import EmployeeJoining, UserProfile,ShiftTime,Attendance,SalaryDetails
from django.db import IntegrityError
from django.contrib.staticfiles import finders
from .models import UserProfile, Quotation
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, F, ExpressionWrapper, fields, DurationField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect ,get_object_or_404
from django.http import HttpResponse
from django.db import IntegrityError
from django.shortcuts import render
from datetime import datetime
from .models import SalaryDetails, Attendance
from django.db.models import Count
import io
from django.shortcuts import render
from django.db.models import Count, F, Sum
from datetime import timedelta

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics

from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from .models import EmployeeJoining, Attendance, BirthdayCompany
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Attendance, EmployeeJoining
from django.views.decorators.http import require_POST
from django.db import IntegrityError


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import Attendance, EmployeeJoining
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import Attendance, EmployeeJoining
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import EmployeeJoining, Attendance
from django.core.exceptions import ValidationError

import inflect






from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(user_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return redirect('login')

            # Allow access if the user is a superuser
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if the user has a profile with the specified user type
            try:
                user_profile = request.user.userprofile
                if user_profile.user_type == user_type:
                    return view_func(request, *args, **kwargs)
                else:
                    raise PermissionDenied
            except UserProfile.DoesNotExist:
                raise PermissionDenied

        return _wrapped_view
    return decorator



def permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)








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



from datetime import date




from collections import defaultdict
from datetime import date
from django.shortcuts import render
from .models import UserProfile, EmployeeJoining, Attendance, BirthdayCompany



@role_required('superuser')
def dashboard(request):
    # Retrieve the selected company from the request (if any)
    company_id = request.GET.get('company_id')
    employees = EmployeeJoining.objects.all() 
    
    # Get all companies for the dropdown
    companies = UserProfile.objects.filter(user_type='company')

    # Initialize variables
    selected_company = None
    total_employees = 0
    employees_present_today = 0
    employees_absent_today = 0
    birthdays = []

    # Get today's date
    today = date.today()

    # If a specific company is selected, filter the data accordingly
    if company_id:
        try:
            selected_company = UserProfile.objects.get(id=company_id, user_type='company')
            employees = EmployeeJoining.objects.filter(company=selected_company)
            employee_ids = employees.values_list('id', flat=True)
            total_employees = employees.count()
            
            # Filter attendance for today's date
            employees_present_today = Attendance.objects.filter(employee_id__in=employee_ids, status='P', date=today).count()
            employees_absent_today = Attendance.objects.filter(employee_id__in=employee_ids, status='A', date=today).count()

            # Filter birthdays for the selected company
            birthdays = BirthdayCompany.objects.filter(user_profile=selected_company).order_by('birthday_date')
        except UserProfile.DoesNotExist:
            # Handle error as needed, e.g., redirect to an error page or set a message
            selected_company = None
    else:
        # If no company is selected, aggregate data for all companies
        total_employees = EmployeeJoining.objects.all().count()
        
        # Filter attendance for today's date across all employees
        employees_present_today = Attendance.objects.filter(status='P', date=today).count()
        employees_absent_today = Attendance.objects.filter(status='A', date=today).count()

        # Get birthdays for all companies
        birthdays = BirthdayCompany.objects.all().order_by('birthday_date')

    # Group birthdays by month and day (ignore the year)
    birthdays_by_date = defaultdict(list)
    for birthday in birthdays:
        birthday_key = (birthday.birthday_date.month, birthday.birthday_date.day)
        birthdays_by_date[birthday_key].append(birthday)

    # Get today's birthdays by month and day
    today_key = (today.month, today.day)
    todays_birthdays = birthdays_by_date.get(today_key, [])

    # Render the dashboard template with the company data and birthday data
    return render(request, 'admin/dashboard.html', {
        'companies': companies,
        'employees':employees,
        'selected_company': selected_company,
        'total_employees': total_employees,
        'employees_present_today': employees_present_today,
        'employees_absent_today': employees_absent_today,
        'birthdays_by_date': birthdays_by_date,
        'todays_birthdays': todays_birthdays,
        'today': today,
    })

















#######################################################################################################################################

@role_required('company')
def company_dashboard(request):
    return render(request, 'company/company_dashboard.html')


from django.shortcuts import render
from datetime import timedelta
from .models import EmployeeJoining, Attendance



@role_required('fo')
def fo_dashboard(request):
    # Get the selected company from the request parameters (if provided)
    company_id = request.GET.get('company_id', '')

    # Fetch all companies for the dropdown filter
    companies = UserProfile.objects.filter(user_type='company')

    # Filter employees based on the selected company
    if company_id:  # If a specific company is selected
        employees = EmployeeJoining.objects.filter(company_id=company_id)
    else:  # If no company is selected, list all employees
        employees = EmployeeJoining.objects.all()

    employee_hours = []

    for employee in employees:
        # Get the number of attendance records with status 'P' (Present)
        num_present_days = Attendance.objects.filter(employee=employee, status='P').count()

        # Get the shift time for the employee, assuming a single shift for simplicity
        shifts = Attendance.objects.filter(employee=employee, status='P').values_list('shift', flat=True).distinct()
        if shifts:
            shift = ShiftTime.objects.filter(id__in=shifts).first()
            shift_time = shift.shift_total_time if shift else timedelta()
        else:
            shift_time = timedelta()

        # Calculate total worked hours
        total_worked_time = num_present_days * shift_time

        employee_hours.append({
            'employee': employee,
            'total_hours': total_worked_time
        })

    return render(request, 'FO/fo_dashboard.html', {
        'employee_hours': employee_hours,
        'companies': companies,          # Pass companies to the template for the filter dropdown
        'selected_company': company_id,    # To know which company is selected
    })




# @role_required('fo')
# def fo_dashboard(request):
#     employees = EmployeeJoining.objects.all()

#     employee_hours = []

#     for employee in employees:
#         # Get the number of attendance records with status 'P' (Present)
#         num_present_days = Attendance.objects.filter(employee=employee, status='P').count()

#         # Get the shift time for the employee, assuming a single shift for simplicity
#         shifts = Attendance.objects.filter(employee=employee, status='P').values_list('shift', flat=True).distinct()
#         if shifts:
#             shift = ShiftTime.objects.filter(id__in=shifts).first()
#             shift_time = shift.shift_total_time if shift else timedelta()
#         else:
#             shift_time = timedelta()

#         # Calculate total worked hours
#         total_worked_time = num_present_days * shift_time

#         employee_hours.append({
#             'employee': employee,
#             'total_hours': total_worked_time
#         })

#     return render(request, 'FO/fo_dashboard.html', {'employee_hours': employee_hours})




#########################################################################################################


from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile

@role_required('superuser')
def add_company(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        gst_or_emergency = request.POST.get('gst_or_emergency')

        # Validate required fields
        if not email or not password or not first_name or not last_name:
            return JsonResponse({'success': False, 'error': 'All fields are required.'})

        try:
            # Create the user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # Create the user profile
            UserProfile.objects.create(
                user=user,
                user_type='company',
                contact=contact,
                gst_or_emergency=gst_or_emergency,
            )
            return JsonResponse({'success': True})  # Respond with success
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})  # Handle errors

    return render(request, 'admin/add_company.html')



from django.shortcuts import render
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import UserProfile
from django.http import JsonResponse
from django.contrib import messages

@role_required('superuser')
def add_fo(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        gst_or_emergency = request.POST.get('gst_or_emergency')

        if not email or not password or not first_name or not last_name:
            return JsonResponse({'success': False, 'error': "All fields are required."})

        try:
            # Create the user and user profile
            user = User.objects.create_user(
                username=email,
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

            return JsonResponse({'success': True})

        except IntegrityError:
            return JsonResponse({'success': False, 'error': "A user with this email already exists."})

    return render(request, 'admin/add_fo.html')





@role_required('company')
def companyList(request):
    companies = UserProfile.objects.filter(user_type='company')
    return render(request, 'admin/companyList.html', {'companies': companies})




from django.shortcuts import render
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from .models import EmployeeJoining, SalaryDetails, UserProfile
from django.core.files.base import ContentFile
 # Assuming you have a utility for generating PDFs
from django.core.files.base import ContentFile
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from .models import EmployeeJoining, SalaryDetails, UserProfile

@role_required('fo')
def add_employee(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Employee data
                emp_id = request.POST['emp_id']
                first_name = request.POST['first_name']
                middle_name = request.POST.get('middle_name', '')
                last_name = request.POST['last_name']
                contact_number = request.POST['contact_number']
                age = request.POST['age']
                gender = request.POST['gender']
                current_address = request.POST['current_address']
                permanent_address = request.POST['permanent_address']
                city = request.POST['city']
                state = request.POST['state']
                pincode = request.POST['pincode']
                date_of_birth = request.POST['date_of_birth']
                emergency_contact1 = request.POST['emergency_contact1']
                emergency_contact_relation1 = request.POST['emergency_contact_relation1']
                emergency_contact_relation1_name = request.POST['emergency_contact_relation1_name']
                pancard = request.POST['pancard']
                aadhar = request.POST['aadhar']
                voter = request.POST['voter']
                security_guard_training = request.POST.get('security_guard_training') == 'yes'
                job_experience = request.POST.get('job_experience') == 'yes'
                profile_picture = request.FILES['profile_picture']
                preferred_work_arrangements = request.POST['preferred_work_arrangements']
                position = request.POST['position']
                account_holder_name = request.POST['account_holder_name']
                bank_name = request.POST['bank_name']
                bank_account_number = request.POST['bank_account_number']
                ifsc_code = request.POST['ifsc_code']
                branch_name = request.POST['branch_name']
                bank_address = request.POST['bank_address']
                qualification = request.POST['qualification']
                experience = request.POST['experience']
                
                # Company data
                company_id = request.POST.get('company')
                company = None
                if company_id:
                    try:
                        company = UserProfile.objects.get(id=company_id, user_type='company')
                    except UserProfile.DoesNotExist:
                        return render(request, 'FO/employee_form.html', {'error': 'Selected company does not exist or is not valid.'})

                # Create EmployeeJoining instance
                employee = EmployeeJoining(
                    emp_id=emp_id,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    contact_number=contact_number,
                    age=age,
                    gender=gender,
                    current_address=current_address,
                    permanent_address=permanent_address,
                    city=city,
                    state=state,
                    pincode=pincode,
                    date_of_birth=date_of_birth,
                    emergency_contact1=emergency_contact1,
                    emergency_contact_relation1=emergency_contact_relation1,
                    emergency_contact_relation1_name=emergency_contact_relation1_name,
                    pancard=pancard,
                    aadhar=aadhar,
                    voter=voter,
                    profile_picture=profile_picture,
                    preferred_work_arrangements=preferred_work_arrangements,
                    position=position,
                    account_holder_name=account_holder_name,
                    bank_name=bank_name,
                    bank_account_number=bank_account_number,
                    ifsc_code=ifsc_code,
                    branch_name=branch_name,
                    bank_address=bank_address,
                    qualification=qualification,
                    experience=experience,
                    company=company,
                )
                employee.save()

                # Create SalaryDetails instance with default values
                salary_details = SalaryDetails(
                    employee=employee,
                    basic_salary=0,
                    special_allowance=0,
                    total=0,
                    conveyance_allowance=0,
                    education_allowance=0,
                    travelling_allowance=0,
                    hours_daily_duty=0,
                    hra=0,
                    pf=0,
                    gratuity=0,
                    leave_with_wages=0,
                    esic=0,
                    paid_holiday=0,
                    bonus=0,
                    uniform=0,
                    total_b=0,
                    total_c=0,
                    # advance_amount=0,
                    food_allowance=0,
                    price_partial_uniform=0,
                    # advance_request_status='Pending',
                    # advance_payment_approval_date=None,
                    actual_salary=0.00,
                    
                    replicated_basic_salary=0,
                    replicated_special_allowance=0,
                    replicated_conveyance_allowance=0,
                    replicated_education_allowance=0,
                    replicated_travelling_allowance=0,
                    replicated_hours_daily_duty=0,
                    replicated_food_allowance=0,
                    replicated_total=0,
                    replicated_total_b=0,
                    replicated_hra=0,
                    replicated_pf=0,
                    replicated_gratuity=0,
                    replicated_leave_with_wages=0,
                    replicated_esic=0,
                    replicated_paid_holiday=0,
                    replicated_bonus=0,
                    replicated_total_c=0,
                    replicated_actual_salary=0,
                )
                salary_details.save()

                # Generate PDF
                pdf_data = generate_employee_pdf(employee)

                # Save PDF to the model instance
                employee.pdf_file.save(f'{employee.emp_id}_details.pdf', ContentFile(pdf_data))

                # Provide the generated PDF for download
                response = HttpResponse(pdf_data, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{employee.emp_id}_details.pdf"'

                return response
        except IntegrityError:
            return render(request, 'FO/employee_form.html', {'error': 'Employee ID already exists. Please use a unique Employee ID.'})

    # If GET request, render the form with a list of companies
    companies = UserProfile.objects.filter(user_type='company')
    
    return render(request, 'FO/employee_form.html', {'companies': companies})














    
from django.http import JsonResponse
from django.shortcuts import render
from .models import UserProfile, BirthdayCompany



@role_required('superuser')
def addbirth(request):
    if request.method == 'POST':
        birthday_date = request.POST.get('birthday_date')
        description = request.POST.get('description')
        company_profile_id = request.POST.get('company')

        if birthday_date and description and company_profile_id:
            try:
                company_profile = UserProfile.objects.get(id=company_profile_id, user_type='company')
                new_birthday = BirthdayCompany.objects.create(
                    user_profile=company_profile,
                    birthday_date=birthday_date,
                    description=description
                )
                # Fetch all birthdays to update the list
                birthdays = BirthdayCompany.objects.all().order_by('birthday_date')
                birthdays_list = []
                for birthday in birthdays:
                    birthdays_list.append({
                        'company': birthday.user_profile.user.email,
                        'birthday_date': birthday.birthday_date,
                        'description': birthday.description,
                        'id': birthday.id
                    })

                return JsonResponse({
                    'success': True,
                    'birthdays': birthdays_list
                })
            except UserProfile.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid company profile.'})
        else:
            return JsonResponse({'success': False, 'error': 'All fields are required.'})
    
    company_profiles = UserProfile.objects.filter(user_type='company')
    birthdays = BirthdayCompany.objects.all().order_by('birthday_date')
    return render(request, 'admin/addbirth.html', {
        'company_profiles': company_profiles,
        'birthdays': birthdays,
    })
    
#######################------------------(Edit, delete birthday (Yash)--------------------------------------##################################################

from django.shortcuts import render, get_object_or_404, redirect
from .models import BirthdayCompany, UserProfile


@role_required('superuser')
def edit_birthday(request, birthday_id):
    birthday = get_object_or_404(BirthdayCompany, id=birthday_id)
    
    if request.method == 'POST':
        birthday_date = request.POST.get('birthday_date')
        description = request.POST.get('description')
        company_profile_id = request.POST.get('company')

        # Validate the input
        if birthday_date and description and company_profile_id:
            try:
                # Retrieve the UserProfile instance with 'company' type
                company_profile = UserProfile.objects.get(id=company_profile_id, user_type='company')
                # Update the existing BirthdayCompany entry
                birthday.birthday_date = birthday_date
                birthday.description = description
                birthday.user_profile = company_profile
                birthday.save()

                return redirect('addbirth')  # Redirect to the list view after saving
            except UserProfile.DoesNotExist:
                return redirect('edit_birthday', birthday_id=birthday_id)  # Redirect to edit page with error
        else:
            return redirect('edit_birthday', birthday_id=birthday_id)  # Redirect to edit page with error
    
    else:
        company_profiles = UserProfile.objects.filter(user_type='company')
        return render(request, 'admin/edit_birthday.html', {
            'birthday': birthday,
            'company_profiles': company_profiles,
        })


from django.shortcuts import redirect, get_object_or_404
from .models import BirthdayCompany

def delete_birthday(request, birthday_id):
    birthday = get_object_or_404(BirthdayCompany, id=birthday_id)
    birthday.delete()
    return redirect('addbirth')  # Redirect to the list view after deletion






import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from django.contrib.staticfiles import finders
from django.http import HttpResponse

def generate_employee_pdf(employee):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Find the font file
    font_path = finders.find('NotoSansDevanagari-VariableFont_wdth,wght.ttf')
    if not font_path:
        raise FileNotFoundError("Font file not found. Please ensure it's placed correctly in the static directory.")

    # Register custom font
    pdfmetrics.registerFont(TTFont('NotoSansDevanagari', font_path))

    # Define custom styles
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(name='CustomStyle', parent=styles['Normal'], fontName='NotoSansDevanagari')
    custom_style1 = ParagraphStyle(name='CustomStyle1', parent=styles['Heading2'], fontName='NotoSansDevanagari')

    # Update default styles
    styles['Heading1'].fontName = 'Helvetica-Bold'
    styles['Heading1'].fontSize = 20
    styles['Heading1'].alignment = 1

    styles['Heading2'].fontName = 'Helvetica-Bold'
    styles['Heading2'].fontSize = 16
    styles['Heading2'].alignment = 1

    styles['Heading4'].fontName = 'Helvetica-Bold'
    styles['Heading4'].fontSize = 12
    styles['Heading4'].alignment = 1

    styles['Normal'].alignment = 1

    # Define image paths
    top_image_path = finders.find('imgs/letter_top.png')
    bottom_image_path = finders.find('imgs/letter_end.png')
    watermark_image_path = finders.find('imgs/logo.png')

    if not top_image_path or not bottom_image_path:
        raise FileNotFoundError("One or both image files were not found.")

    # Create a PDF elements
    elements = []

    def add_page(canvas, doc):
        # Draw top image
        canvas.drawImage(top_image_path, 0, letter[1] - 100, width=letter[0], height=100)

        # Draw bottom image
        canvas.drawImage(bottom_image_path, 0, 0, width=letter[0], height=50)

        # Add watermark in the center
        canvas.saveState()
        width, height = letter  # Get page dimensions
        canvas.setFillAlpha(0.15)  # Set transparency level
        canvas.drawImage(watermark_image_path, width / 4, height / 4, width=width / 2, height=height / 2, mask='auto')
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page, onLaterPages=add_page)

    # Add headings and spacers
    
    elements.append(Spacer(1, 35))

    # Add heading "Joining Form"
    elements.append(Paragraph("Joining Form", styles['Title']))
    elements.append(Spacer(1, 12))

    # Profile Picture
    profile_img = None
    if employee.profile_picture:
        profile_img = Image(employee.profile_picture, width=1*inch, height=1*inch)
    
    profile_picture_box = Table([[profile_img if profile_img else '']], colWidths=[100])
    profile_picture_box.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, 'black'),
    ]))

    # Employee details table
    # Define the employee details as Paragraph elements
    # Define the employee details as key-value pairs
    employee_details_table = Table(
    [
        [
            Paragraph("<b>नाव:</b>", custom_style1),
            Paragraph(f"{employee.first_name} {employee.middle_name} {employee.last_name}", custom_style1),
        ],
        [
            Paragraph("<b>पालकांचे नाव:</b>", custom_style1),
            Paragraph(f"{employee.middle_name} {employee.last_name}", custom_style1),
        ],
        [
            Paragraph("<b>सध्याचा पत्ता:</b>", custom_style1),
            Paragraph(f"{employee.current_address}", custom_style1),
        ],
        [
            Paragraph("<b>स्थायी पत्ता:</b>", custom_style1),
            Paragraph(f"{employee.permanent_address}", custom_style1),
        ],
    ],
    colWidths=[90, 410]  # Adjust column widths to control spacing
    )

    # Apply table styles for alignment and padding
    employee_details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Remove padding from key column
        ('LEFTPADDING', (1, 0), (1, -1), 20),  # Add padding to the value column
        ('NOSPLIT', (0, 0), (-1, -1)),
    ]))


    # Combine profile picture box and employee details table
    profile_and_details_data = [
        [employee_details_table, profile_picture_box]
    ]
    profile_and_details_table = Table(profile_and_details_data, colWidths=[400, 100])
    profile_and_details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(profile_and_details_table)
    elements.append(Spacer(1, 12))

    # Contact Number section
    contact_number_section_data = [
        [
            Paragraph("<b>मोबाईल क्रमांक:</b>", custom_style1),
            Table([[Paragraph(f"<b>{digit}</b>", styles['Normal']) for digit in str(employee.contact_number)]], colWidths=[30]*10, style=[
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 1, 'black'),
                ('BOX', (0, 0), (-1, -1), 1, 'black'),
            ])
        ]
    ]
    
    contact_number_section_table = Table(contact_number_section_data, colWidths=[100, 400])
    contact_number_section_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(contact_number_section_table)
    elements.append(Spacer(1, 12))

    # Married Status
    married_status_data = [
        [
            Paragraph("<b>वैवाहिक स्थिती:</b>", custom_style1),
            Paragraph("Yes" if employee.security_guard_training else "No", styles['Heading3']),
        ]
    ]
    
    married_status_table = Table(married_status_data, colWidths=[100, 400])
    married_status_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(married_status_table)
    elements.append(Spacer(1, 12))

    # Qualification
    qualification_data = [
        [
            Paragraph("<b>शिक्षण:</b>", custom_style1),
            Paragraph(employee.qualification, styles['Heading3']),
        ]
    ]
    
    qualification_data_table = Table(qualification_data, colWidths=[100, 400])
    qualification_data_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(qualification_data_table)
    elements.append(Spacer(1, 12))

    # Birth Date
    birth_data = [
        [
            Paragraph("<b>जन्मतारीख:</b>", custom_style1),
            Paragraph(employee.date_of_birth, styles['Heading3']),
        ]
    ]
    
    birth_table = Table(birth_data, colWidths=[100, 400])
    birth_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(birth_table)
    elements.append(Spacer(1, 12))

    # Document Details
    document_data = [
        [
            Paragraph("<b>Pancard:</b>", custom_style1),
            Paragraph("Yes" if employee.pancard else "No", styles['Heading3']),
        ],
        [
            Paragraph("<b>Aadhar Card:</b>", custom_style1),
            Paragraph("Yes" if employee.aadhar else "No", styles['Heading3']),
        ],
        [
            Paragraph("<b>Voter ID:</b>", custom_style1),
            Paragraph("Yes" if employee.voter else "No", styles['Heading3']),
        ]
    ]
    
    document_table = Table(document_data, colWidths=[100, 400])
    document_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(document_table)
    elements.append(Spacer(1, 36))

    # Emergency Contact
    elements.append(Paragraph("<b>Emergency Contact Information</b>", styles['Heading1']))
    elements.append(Spacer(1, 18))

    emergency_contact_data = [
    ["नाव", "मोबाईल क्रमांक", "नाते"],
    [employee.emergency_contact_relation1_name, employee.emergency_contact1, employee.emergency_contact_relation1],
    ]

    # Create the table with specified column widths
    emergency_contact_table = Table(emergency_contact_data, colWidths=[2.5*inch, 2*inch, 2.5*inch])

    # Define the table style including header style
    emergency_contact_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Set background color for header row
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Set text color for header row
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansDevanagari'),  # Set font for header row
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ]))


    elements.append(emergency_contact_table)
    elements.append(Spacer(1, 90))
    elements.append(Spacer(1, 30))

    # Rules
    elements.append(Paragraph("<b>नियम व अटी :</b>", custom_style1))
    elements.append(Spacer(1, 9))

    dummy_rules = [
        "१) १५ दिवसांच्या आत काम सोडल्यास पेमेंट मिळणार नाही.",
        "२) न सांगता ड्युटीवर न आल्यास पर डे १००/- दंड बसेल.",
        "३) ड्युटीवर दारु पिऊन आल्यास कुठल्याही प्रकारचे पेमेंट मिळणार नाही व कामावरुन कमी करण्यास येईल.",
        "४) न सांगता ४ दिवस ड्युटीवरती न आल्यास कामावरून कमी करण्यात येईल.",
        "५) ड्युटीवर असताना पुर्ण युनिफार्म असणे बंधनकारक आहे.",
        "६) काम सोडायचे असल्यास १५ दिवस आगोदर राजीनामा देणे बंधनकारक आहे. न दिल्यास पहिले काम केलेले पेमेंट मिळणार नाही.",
        "७) कामावरती कुठल्याही प्रकारचे गैरवर्तन आढळल्यास लगेच कामावरून कमी करण्यात येईल.",
        "८) संस्थेची नोकरी कायमस्वरुपी नाही हे मला माहित आहे. संस्थेकडील ज्या कंत्राटामध्ये मी कामवर असेल ते कंत्राट बंद झाल्यास व दुसऱ्या ठिकाणी जागा रिकामी नसल्यास मला नोकरी वरुन काढले जाईल हे मला मान्य आहे.",
        "१) ड्युटीवर असताना झोपेत सापडल्यास ५००/- दंड बसेल.",
        "१०) कंपनीने दिलेले हे सर्व नियम मला मान्य आहेत.",



        
    ]

    for rule in enumerate(dummy_rules):
        elements.append(Paragraph(f"{rule[1]}", custom_style))
        elements.append(Spacer(1, 6))

    # Fingerprints
    elements.append(Paragraph("<b>Left Finger</b>", styles['Heading3']))
    elements.append(Spacer(1, 6))

    left_finger_data = [["" for _ in range(5)]]
    left_finger_table = Table(left_finger_data, colWidths=[1*inch]*5, rowHeights=[1*inch])
    left_finger_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(left_finger_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Right Finger</b>", styles['Heading3']))
    elements.append(Spacer(1, 6))

    right_finger_data = [["" for _ in range(5)]]
    right_finger_table = Table(right_finger_data, colWidths=[1*inch]*5, rowHeights=[1*inch])
    right_finger_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(right_finger_table)
    elements.append(Spacer(1, 72))

    # Signature section
    signature_table_data = [
        [
            Paragraph("<b>Date:</b> ___________________", styles['Normal']),
            Paragraph("<b>Signature:</b> ___________________", styles['Normal']),
        ]
    ]
    signature_table = Table(signature_table_data, colWidths=[200, 200])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0, 'white'),
    ]))

    elements.append(signature_table)

    # Build PDF
    doc.build(elements, onFirstPage=add_page, onLaterPages=add_page)
    pdf_value = buffer.getvalue()
    buffer.close()

    return pdf_value





@role_required('fo')
def create_quotation(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        sr_no_list = request.POST.getlist('sr_no[]')
        description_list = request.POST.getlist('description[]')
        price_list = request.POST.getlist('price[]')

        # Generate the PDF
        pdf_buffer = generate_quotation_pdf(company_name, sr_no_list, description_list, price_list)

        # Return PDF as response
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="quotation.pdf"'
        return response
    else:
        return render(request, 'FO/create_quotation.html')
    

from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_quotation_pdf(company_name, sr_no_list, description_list, price_list):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%d-%m-%Y")


    # Paths to images
    top_image_path = finders.find('imgs/letter_top.png')  # Path to the top image
    bottom_image_path = finders.find('imgs/letter_end.png')  # Path to the bottom image

    if not top_image_path or not bottom_image_path:
        raise FileNotFoundError("One or both image files were not found.")

    # Image dimensions
    top_image_height = 100  # Adjust the height as needed
    bottom_image_height = 50  # Adjust the height as needed

    # Draw the top image
    p.drawImage(top_image_path, 0, height - top_image_height, width=width, height=top_image_height)

    # Draw the bottom image
    p.drawImage(bottom_image_path, 0, 0, width=width, height=bottom_image_height)

    # Define margins for content
    top_margin = top_image_height + 10  # Space below the top image
    bottom_margin = bottom_image_height + 10  # Space above the bottom image

    # Define available content height
    content_start_y = height - top_margin
    content_end_y = bottom_margin

    # Set up fonts
    p.setFont("Times-Roman", 12)

    # Add company name
    p.drawString(100, content_start_y - 30, f"To: {company_name}")

    # Add subject
    p.drawString(100, content_start_y - 50, "Subject: Quotation for Security Guards")
    p.saveState()
    

    # Add salutation
    p.drawString(100, content_start_y - 70, "Dear Sir/Madam,")

    # Add introduction paragraph with manual line breaks
    intro_lines = [
        "                   We are pleased to submit our quotation for providing Security Supervisor,",
        "Housekeeping and Security Guards to your esteemed organization. We are committed",
        "to delivering services of the highest quality and we are looking formard to the overall",
        "success of your operations.We look forward to establishing a long-term partnership ",
        "with you. "
    ]

    line_height = 14  # Adjust line height if needed
    for i, line in enumerate(intro_lines):
        p.drawString(100, content_start_y - 110 - i * line_height, line)

    p.drawString(100, content_start_y - 200, "Below is the quotation for Security Services")
    # Draw the table
    table_start_y = content_start_y - 210  # Adjusted to make space for the paragraph
    col_widths = [50, 240, 160]  # Adjust the column widths
    row_height = 20

    # Create a grid for the table headers
    table_x = 90
    p.grid([table_x, table_x + col_widths[0], table_x + col_widths[0] + col_widths[1], 
            table_x + col_widths[0] + col_widths[1] + col_widths[2]], 
           [table_start_y, table_start_y - row_height])

    # Add headers
    p.drawString(table_x + 10, table_start_y - row_height + 5, "Sr. No.")
    p.drawString(table_x + col_widths[0] + 10, table_start_y - row_height + 5, "Description")
    p.drawString(table_x + col_widths[0] + col_widths[1] + 10, table_start_y - row_height + 5, "30/31 Days")

    # Draw the table content with grid
    table_y = table_start_y - row_height
    for sr_no, description, price in zip(sr_no_list, description_list, price_list):
        table_y -= row_height

        # Create a grid for each row
        p.grid([table_x, table_x + col_widths[0], table_x + col_widths[0] + col_widths[1], 
                table_x + col_widths[0] + col_widths[1] + col_widths[2]], 
               [table_y, table_y + row_height])

        # Add content
        p.drawString(table_x + 10, table_y + 5, str(sr_no))
        p.drawString(table_x + col_widths[0] + 10, table_y + 5, description)
        try:
            price = float(price)
        except ValueError:
            price = 0.0  # Handle invalid price formats gracefully
        p.drawString(table_x + col_widths[0] + col_widths[1] + 10, table_y + 5, f"Rs. {price:.2f} (12 Hrs)")
    # Add GST notice
    gst_notice = "18% GST will be applicable on overall billing."
    p.drawString(100, table_y - 20, gst_notice)

    # Add thank you note
    thank_you_note = "Thank you,"
    p.drawString(width - 100 - 100, bottom_margin + 300, thank_you_note)  # Align right
    company = "Best Security"
    p.drawString(width - 100 - 100, bottom_margin + 280, company) 
    p.drawString(width - 100 - 40, bottom_margin + 660, f"Date: {formatted_date}") 

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer




@login_required
def createquotation(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        sr_no_list = request.POST.getlist('sr_no[]')
        description_list = request.POST.getlist('description[]')
        price_list = request.POST.getlist('price[]')

        # Generate the PDF
        pdf_buffer = generate_quotation_pdf(company_name, sr_no_list, description_list, price_list)

        # Return PDF as response
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="quotation.pdf"'
        return response
    else:
        return render(request, 'admin/createquotation.html')
    

from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_quotation_pdf(company_name, sr_no_list, description_list, price_list):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%d-%m-%Y")


    # Paths to images
    top_image_path = finders.find('imgs/letter_top.png')  # Path to the top image
    bottom_image_path = finders.find('imgs/letter_end.png')  # Path to the bottom image

    if not top_image_path or not bottom_image_path:
        raise FileNotFoundError("One or both image files were not found.")

    # Image dimensions
    top_image_height = 100  # Adjust the height as needed
    bottom_image_height = 50  # Adjust the height as needed
    p.setFont("Times-Roman", 12)
    # Draw the top image
    p.drawImage(top_image_path, 0, height - top_image_height, width=width, height=top_image_height)

    # Draw the bottom image
    p.drawImage(bottom_image_path, 0, 0, width=width, height=bottom_image_height)

    # Define margins for content
    top_margin = top_image_height + 10  # Space below the top image
    bottom_margin = bottom_image_height + 10  # Space above the bottom image

    # Define available content height
    content_start_y = height - top_margin
    content_end_y = bottom_margin

    p.saveState()
    watermark = finders.find('imgs/logo.png')
    p.setFillAlpha(0.15)  # Set transparency level
    p.drawImage(str(watermark), width / 4, height / 4, width=width / 2, height=height / 2, mask='auto')
    p.restoreState()
   
    # Set up fonts 

    # Add company name
    p.drawString(100, content_start_y - 30, f"To: {company_name}")

    # Add subject
    p.drawString(100, content_start_y - 50, "Subject: Quotation for Security Guards")

    # Add salutation
    p.drawString(100, content_start_y - 70, "Dear Sir/Madam,")

    # Add introduction paragraph with manual line breaks
    intro_lines = [
        "                   We are pleased to submit our quotation for providing Security Supervisor,",
        "Housekeeping and Security Guards to your esteemed organization. We are committed",
        "to delivering services of the highest quality and we are looking formard to the overall",
        "success of your operations.We look forward to establishing a long-term partnership ",
        "with you. "
    ]

    line_height = 14  # Adjust line height if needed
    for i, line in enumerate(intro_lines):
        p.drawString(100, content_start_y - 110 - i * line_height, line)

    p.drawString(100, content_start_y - 200, "Below is the quotation for Security Services")
    # Draw the table
    table_start_y = content_start_y - 210  # Adjusted to make space for the paragraph
    col_widths = [50, 240, 140]  # Adjust the column widths
    row_height = 20

    # Create a grid for the table headers
    table_x = 90
    p.grid([table_x, table_x + col_widths[0], table_x + col_widths[0] + col_widths[1], 
            table_x + col_widths[0] + col_widths[1] + col_widths[2]], 
           [table_start_y, table_start_y - row_height])

    # Add headers
    p.drawString(table_x + 10, table_start_y - row_height + 5, "Sr. No.")
    p.drawString(table_x + col_widths[0] + 10, table_start_y - row_height + 5, "Description")
    p.drawString(table_x + col_widths[0] + col_widths[1] + 10, table_start_y - row_height + 5, "30/31 Days")

    # Draw the table content with grid
    table_y = table_start_y - row_height
    for sr_no, description, price in zip(sr_no_list, description_list, price_list):
        table_y -= row_height

        # Create a grid for each row
        p.grid([table_x, table_x + col_widths[0], table_x + col_widths[0] + col_widths[1], 
                table_x + col_widths[0] + col_widths[1] + col_widths[2]], 
               [table_y, table_y + row_height])

        # Add content
        p.drawString(table_x + 10, table_y + 5, str(sr_no))
        p.drawString(table_x + col_widths[0] + 10, table_y + 5, description)
        try:
            price = float(price)
        except ValueError:
            price = 0.0  # Handle invalid price formats gracefully
        p.drawString(table_x + col_widths[0] + col_widths[1] + 10, table_y + 5, f"Rs. {price:.2f} (12 Hrs)")
    # Add GST notice
    gst_notice = "18% GST will be applicable on overall billing."
    p.drawString(100, table_y - 20, gst_notice)

    # Add thank you note
    thank_you_note = "Thank you,"
    p.drawString(width - 100 - 100, bottom_margin + 300, thank_you_note)  # Align right
    company = "Best Security"
    p.drawString(width - 100 - 100, bottom_margin + 280, company) 
    p.drawString(width - 100 - 40, bottom_margin + 660, f"Date: {formatted_date}") 

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer





from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ShiftTime
from datetime import datetime


@role_required('fo')
def addshift(request):
    if request.method == 'POST':
        try:
            intime = request.POST.get('intime')
            outtime = request.POST.get('outtime')
            description = request.POST.get('description')

            # Convert intime and outtime to datetime objects
            intime_dt = datetime.strptime(intime, '%H:%M')
            outtime_dt = datetime.strptime(outtime, '%H:%M')

            # Calculate total time in hours
            time_difference = outtime_dt - intime_dt
            shift_total_time = abs(time_difference.total_seconds()) / 3600

            # Create a new ShiftTime object and save it to the database
            ShiftTime.objects.create(
                intime=intime,
                outtime=outtime,
                description=description,
                shift_total_time=shift_total_time
            )

            # Return success response
            return JsonResponse({'success': True})

        except Exception as e:
            # Return error response
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Handle GET request by rendering the form
    return render(request, 'FO/addshift.html')


def shift_list(request):
    shifts = ShiftTime.objects.all()  # Fetch all ShiftTime records
    return render(request, 'FO/shift_list.html', {'shifts': shifts})



from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import EmployeeJoining, ShiftTime, Attendance, UserProfile



def markattendance(request):
    if request.method == 'GET':
        company_id = request.GET.get('company', None)
        date = request.GET.get('date', timezone.now().date())

        companies = UserProfile.objects.filter(user_type='company')

        if company_id:
            try:
                company = UserProfile.objects.get(id=company_id, user_type='company')
                employees = EmployeeJoining.objects.filter(company=company)
                shifts = ShiftTime.objects.all()
            except UserProfile.DoesNotExist:
                messages.error(request, "Company not found")
                employees = []
                shifts = []
        else:
            employees = []
            shifts = []

        context = {
            'date': date,
            'company_id': company_id,
            'employees': employees,
            'shifts': shifts,
            'companies': companies,
        }

        return render(request, 'FO/markattendance.html', context)

    elif request.method == 'POST':
        employee_id = request.POST.get('employee')
        date = request.POST.get('date')
        check_in_time = request.POST.get('check_in_time')
        check_out_time = request.POST.get('check_out_time')
        status = request.POST.get('status')
        shift_name = request.POST.get('shift')
        notes = request.POST.get('notes', '')

        try:
            employee = EmployeeJoining.objects.get(id=employee_id)
            shift = ShiftTime.objects.get(name=shift_name)  # Retrieve ShiftTime instance by name

            # Create a new attendance record
            Attendance.objects.create(
                employee=employee,
                date=date,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                status=status,
                shift=shift,
                notes=notes
            )

            messages.success(request, "Attendance marked successfully!")
        except EmployeeJoining.DoesNotExist:
            messages.error(request, "Employee not found")
        except ShiftTime.DoesNotExist:
            messages.error(request, "Shift not found")
        except Exception as e:
            messages.error(request, f"Failed to mark attendance: {e}")

        return redirect('markattendance')  # Adjust redirect as needed

from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from .models import Attendance, ShiftTime

def submit_attendance(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        company_id = request.POST.get('company')

        if not date or not company_id:
            return HttpResponseBadRequest("Missing date or company")

        # Process each employee
        for employee_id in request.POST.getlist('employee_ids'):  # Make sure employee IDs are included in the form
            status = request.POST.get(f'status_{employee_id}')
            shift_id = request.POST.get(f'shift_{employee_id}')
            notes = request.POST.get(f'notes_{employee_id}')

            if not shift_id:  # Validate shift_id
                continue  # Skip if no shift_id is provided

            try:
                shift = ShiftTime.objects.get(id=shift_id)
                intime = shift.intime
                outtime = shift.outtime
            except ShiftTime.DoesNotExist:
                intime = None
                outtime = None  # Handle this case appropriately

            # Create a new attendance record
            Attendance.objects.create(
                employee_id=employee_id,
                date=date,
                status=status,
                shift=shift,
                check_in_time=intime,
                check_out_time=outtime,
                notes=notes
            )

        return redirect('markattendance')
    else:
        return HttpResponseBadRequest("Invalid request method")    












from io import BytesIO
from .models import Quotations
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render
from .models import Quotations

@role_required('superuser')
def quotation(request):
    if request.method == 'POST':
        # Extract data from POST request
        company = request.POST.get('company')
        guard_basic_pay = request.POST.get('guard_basic_pay')
        guard_special_allowance = request.POST.get('guard_special_allowance')
        guard_total_a = request.POST.get('guard_total_a')
        guard_conveyance_allowance = request.POST.get('guard_conveyance_allowance')
        guard_education_allowance = request.POST.get('guard_education_allowance')
        guard_travelling_allowance = request.POST.get('guard_travelling_allowance')
        guard_house_duty = request.POST.get('guard_house_duty')
        guard_total_b = request.POST.get('guard_total_b')
        guard_washing_allowance = request.POST.get('guard_washing_allowance')
        guard_hra = request.POST.get('guard_hra')
        guard_sub_total_c = request.POST.get('guard_sub_total_c')
        guard_pf = request.POST.get('guard_pf')
        guard_gratuity = request.POST.get('guard_gratuity')
        guard_leave_with_wages = request.POST.get('guard_leave_with_wages')
        guard_esic = request.POST.get('guard_esic')
        guard_paid_holiday = request.POST.get('guard_paid_holiday')
        guard_bonus = request.POST.get('guard_bonus')
        guard_uniform = request.POST.get('guard_uniform')
        # guard_charges = request.POST.get('guard_charges')
        guard_total_c = request.POST.get('guard_total_c')
        guard_service_charges = request.POST.get('guard_service_charges')
        guard_grand_total_per_month = request.POST.get('guard_grand_total_per_month')

        # Repeat the same for supervisor fields
        supervisor_basic_pay = request.POST.get('supervisor_basic_pay')
        supervisor_special_allowance = request.POST.get('supervisor_special_allowance')
        supervisor_total_a = request.POST.get('supervisor_total_a')
        supervisor_conveyance_allowance = request.POST.get('supervisor_conveyance_allowance')
        supervisor_education_allowance = request.POST.get('supervisor_education_allowance')
        supervisor_travelling_allowance = request.POST.get('supervisor_travelling_allowance')
        supervisor_house_duty = request.POST.get('supervisor_house_duty')
        supervisor_total_b = request.POST.get('supervisor_total_b')
        supervisor_washing_allowance = request.POST.get('supervisor_washing_allowance')
        supervisor_hra = request.POST.get('supervisor_hra')
        supervisor_sub_total_c = request.POST.get('supervisor_sub_total_c')
        supervisor_pf = request.POST.get('supervisor_pf')
        supervisor_gratuity = request.POST.get('supervisor_gratuity')
        supervisor_leave_with_wages = request.POST.get('supervisor_leave_with_wages')
        supervisor_esic = request.POST.get('supervisor_esic')
        supervisor_paid_holiday = request.POST.get('supervisor_paid_holiday')
        supervisor_bonus = request.POST.get('supervisor_bonus')
        supervisor_uniform = request.POST.get('supervisor_uniform')
        # supervisor_charges = request.POST.get('supervisor_charges')
        supervisor_total_c = request.POST.get('supervisor_total_c')
        supervisor_service_charges = request.POST.get('supervisor_service_charges')
        supervisor_grand_total_per_month = request.POST.get('supervisor_grand_total_per_month')

        # Save to database
        quotation = Quotations(
            company=company,
            guard_basic_pay=guard_basic_pay,
            guard_special_allowance=guard_special_allowance,
            guard_total_a=guard_total_a,
            guard_conveyance_allowance=guard_conveyance_allowance,
            guard_education_allowance=guard_education_allowance,
            guard_travelling_allowance=guard_travelling_allowance,
            guard_house_duty=guard_house_duty,
            guard_total_b=guard_total_b,
            guard_washing_allowance=guard_washing_allowance,
            guard_hra=guard_hra,
            guard_sub_total_c=guard_sub_total_c,
            guard_pf=guard_pf,
            guard_gratuity=guard_gratuity,
            guard_leave_with_wages=guard_leave_with_wages,
            guard_esic=guard_esic,
            guard_paid_holiday=guard_paid_holiday,
            guard_bonus=guard_bonus,
            guard_uniform=guard_uniform,
            # guard_charges=guard_charges,
            guard_total_c=guard_total_c,
            guard_service_charges=guard_service_charges,
            guard_grand_total_per_month=guard_grand_total_per_month,

            supervisor_basic_pay=supervisor_basic_pay,
            supervisor_special_allowance=supervisor_special_allowance,
            supervisor_total_a=supervisor_total_a,
            supervisor_conveyance_allowance=supervisor_conveyance_allowance,
            supervisor_education_allowance=supervisor_education_allowance,
            supervisor_travelling_allowance=supervisor_travelling_allowance,
            supervisor_house_duty=supervisor_house_duty,
            supervisor_total_b=supervisor_total_b,
            supervisor_washing_allowance=supervisor_washing_allowance,
            supervisor_hra=supervisor_hra,
            supervisor_sub_total_c=supervisor_sub_total_c,
            supervisor_pf=supervisor_pf,
            supervisor_gratuity=supervisor_gratuity,
            supervisor_leave_with_wages=supervisor_leave_with_wages,
            supervisor_esic=supervisor_esic,
            supervisor_paid_holiday=supervisor_paid_holiday,
            supervisor_bonus=supervisor_bonus,
            supervisor_uniform=supervisor_uniform,
            # supervisor_charges=supervisor_charges,
            supervisor_total_c=supervisor_total_c,
            supervisor_service_charges=supervisor_service_charges,
            supervisor_grand_total_per_month=supervisor_grand_total_per_month
        )
        quotation.save()
        
        # Generate PDF
        pdf = generate_quotation_pdf1(quotation)
        pdf_file = ContentFile(pdf, 'quotation.pdf')
        quotation.pdf_file.save('quotation.pdf', pdf_file)
        quotation.save()

        # Return the PDF as a downloadable response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="quotation.pdf"'
        return response

    return render(request, 'admin/quotation.html')


from django.http import HttpResponse, FileResponse
from django.db.models import Q


@role_required('superuser')
def quotation_list(request):
    # Define a Q object to filter quotations where at least one supervisor field is greater than zero
    supervisor_q = Q(supervisor_basic_pay__gt=0) | \
                   Q(supervisor_special_allowance__gt=0) | \
                   Q(supervisor_total_a__gt=0) | \
                   Q(supervisor_conveyance_allowance__gt=0) | \
                   Q(supervisor_education_allowance__gt=0) | \
                   Q(supervisor_travelling_allowance__gt=0) | \
                   Q(supervisor_house_duty__gt=0) | \
                   Q(supervisor_total_b__gt=0) | \
                   Q(supervisor_washing_allowance__gt=0) | \
                   Q(supervisor_hra__gt=0) | \
                   Q(supervisor_sub_total_c__gt=0) | \
                   Q(supervisor_pf__gt=0) | \
                   Q(supervisor_gratuity__gt=0) | \
                   Q(supervisor_leave_with_wages__gt=0) | \
                   Q(supervisor_esic__gt=0) | \
                   Q(supervisor_paid_holiday__gt=0) | \
                   Q(supervisor_bonus__gt=0) | \
                   Q(supervisor_uniform__gt=0) | \
                   Q(supervisor_total_c__gt=0) | \
                   Q(supervisor_service_charges__gt=0) | \
                   Q(supervisor_grand_total_per_month__gt=0)

    # Retrieve quotations where at least one supervisor field is greater than zero
    quotations_with_supervisor = Quotations.objects.filter(supervisor_q)
    
    # Retrieve quotations where all supervisor fields are zero
    quotations_without_supervisor = Quotations.objects.exclude(supervisor_q)
    
    return render(request, 'admin/quotation_list.html', {
        'quotations_with_supervisor': quotations_with_supervisor,
        'quotations_without_supervisor': quotations_without_supervisor
    })

def view_quotation_pdf(request, pk):
    quotation = get_object_or_404(Quotations, pk=pk)
    if quotation.pdf_file:
        return FileResponse(quotation.pdf_file, content_type='application/pdf')
    return HttpResponse("PDF not found.", status=404)


# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Quotation

from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

def update_quotation(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if not id:
            return HttpResponse('Quotation ID is required.', status=400)
        
        quotation = get_object_or_404(Quotations, pk=id)
        print("POST Data:", request.POST)
        
        # Log initial state
        logger.info(f'Updating Quotation ID {id} with POST data: {request.POST}')

        # Update fields from POST data
        quotation.company = request.POST.get('company', quotation.company)
        
        # Guard fields
        quotation.guard_basic_pay = request.POST.get('guard_basic_pay', quotation.guard_basic_pay)
        quotation.guard_special_allowance = request.POST.get('guard_special_allowance', quotation.guard_special_allowance)
        quotation.guard_total_a = request.POST.get('guard_total_a', quotation.guard_total_a)
        quotation.guard_conveyance_allowance = request.POST.get('guard_conveyance_allowance', quotation.guard_conveyance_allowance)
        quotation.guard_education_allowance = request.POST.get('guard_education_allowance', quotation.guard_education_allowance)
        quotation.guard_travelling_allowance = request.POST.get('guard_travelling_allowance', quotation.guard_travelling_allowance)
        quotation.guard_house_duty = request.POST.get('guard_house_duty', quotation.guard_house_duty)
        quotation.guard_total_b = request.POST.get('guard_total_b', quotation.guard_total_b)
        quotation.guard_washing_allowance = request.POST.get('guard_washing_allowance', quotation.guard_washing_allowance)
        quotation.guard_hra = request.POST.get('guard_hra', quotation.guard_hra)
        quotation.guard_sub_total_c = request.POST.get('guard_sub_total_c', quotation.guard_sub_total_c)
        quotation.guard_pf = request.POST.get('guard_pf', quotation.guard_pf)
        quotation.guard_gratuity = request.POST.get('guard_gratuity', quotation.guard_gratuity)
        quotation.guard_leave_with_wages = request.POST.get('guard_leave_with_wages', quotation.guard_leave_with_wages)
        quotation.guard_esic = request.POST.get('guard_esic', quotation.guard_esic)
        quotation.guard_paid_holiday = request.POST.get('guard_paid_holiday', quotation.guard_paid_holiday)
        quotation.guard_bonus = request.POST.get('guard_bonus', quotation.guard_bonus)
        quotation.guard_uniform = request.POST.get('guard_uniform', quotation.guard_uniform)
        quotation.guard_total_c = request.POST.get('guard_total_c', quotation.guard_total_c)
        quotation.guard_service_charges = request.POST.get('guard_service_charges', quotation.guard_service_charges)
        quotation.guard_grand_total_per_month = request.POST.get('guard_grand_total_per_month', quotation.guard_grand_total_per_month)
        
        # Supervisor fields
        quotation.supervisor_basic_pay = request.POST.get('supervisor_basic_pay', quotation.supervisor_basic_pay)
        print(f"basic pay: {quotation.supervisor_basic_pay}")
        quotation.supervisor_special_allowance = request.POST.get('supervisor_special_allowance', quotation.supervisor_special_allowance)
        quotation.supervisor_total_a = request.POST.get('supervisor_total_a', quotation.supervisor_total_a)
        quotation.supervisor_conveyance_allowance = request.POST.get('supervisor_conveyance_allowance', quotation.supervisor_conveyance_allowance)
        quotation.supervisor_education_allowance = request.POST.get('supervisor_education_allowance', quotation.supervisor_education_allowance)
        quotation.supervisor_travelling_allowance = request.POST.get('supervisor_travelling_allowance', quotation.supervisor_travelling_allowance)
        quotation.supervisor_house_duty = request.POST.get('supervisor_house_duty', quotation.supervisor_house_duty)
        quotation.supervisor_total_b = request.POST.get('supervisor_total_b', quotation.supervisor_total_b)
        quotation.supervisor_washing_allowance = request.POST.get('supervisor_washing_allowance', quotation.supervisor_washing_allowance)
        quotation.supervisor_hra = request.POST.get('supervisor_hra', quotation.supervisor_hra)
        quotation.supervisor_sub_total_c = request.POST.get('supervisor_sub_total_c', quotation.supervisor_sub_total_c)
        quotation.supervisor_pf = request.POST.get('supervisor_pf', quotation.supervisor_pf)
        quotation.supervisor_gratuity = request.POST.get('supervisor_gratuity', quotation.supervisor_gratuity)
        quotation.supervisor_leave_with_wages = request.POST.get('supervisor_leave_with_wages', quotation.supervisor_leave_with_wages)
        quotation.supervisor_esic = request.POST.get('supervisor_esic', quotation.supervisor_esic)
        quotation.supervisor_paid_holiday = request.POST.get('supervisor_paid_holiday', quotation.supervisor_paid_holiday)
        quotation.supervisor_bonus = request.POST.get('supervisor_bonus', quotation.supervisor_bonus)
        quotation.supervisor_uniform = request.POST.get('supervisor_uniform', quotation.supervisor_uniform)
        quotation.supervisor_total_c = request.POST.get('supervisor_total_c', quotation.supervisor_total_c)
        quotation.supervisor_service_charges = request.POST.get('supervisor_service_charges', quotation.supervisor_service_charges)
        quotation.supervisor_grand_total_per_month = request.POST.get('supervisor_grand_total_per_month', quotation.supervisor_grand_total_per_month)

        # Log updated state
        logger.info(f'Updated Quotation: {quotation}')

        # Generate a new PDF
        try:
            pdf_bytes = generate_quotation_pdf1(quotation)
            pdf_file = ContentFile(pdf_bytes, name=f'{quotation.company}_updated.pdf')
            quotation.pdf_file.save(f'{quotation.company}_updated.pdf', pdf_file)
        except Exception as e:
            logger.error(f'Error generating PDF: {e}')
            return HttpResponse('Error generating PDF.', status=500)
        
        # Save the updated quotation
        try:
            quotation.save()
        except Exception as e:
            logger.error(f'Error saving quotation: {e}')
            return HttpResponse('Error saving quotation.', status=500)

        return HttpResponse('Quotation updated successfully!')

    return HttpResponse('Invalid request method.', status=405)





def security_update_quotation(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if not id:
            return HttpResponse('Quotation ID is required.', status=400)
        
        quotation = get_object_or_404(Quotations, pk=id)
        print("POST Data:", request.POST)
        
        # Log initial state
        logger.info(f'Updating Quotation ID {id} with POST data: {request.POST}')

        # Update fields from POST data
        quotation.company = request.POST.get('company', quotation.company)
        
        # Guard fields
        quotation.guard_basic_pay = request.POST.get('guard_basic_pay', quotation.guard_basic_pay)
        quotation.guard_special_allowance = request.POST.get('guard_special_allowance', quotation.guard_special_allowance)
        quotation.guard_total_a = request.POST.get('guard_total_a', quotation.guard_total_a)
        quotation.guard_conveyance_allowance = request.POST.get('guard_conveyance_allowance', quotation.guard_conveyance_allowance)
        quotation.guard_education_allowance = request.POST.get('guard_education_allowance', quotation.guard_education_allowance)
        quotation.guard_travelling_allowance = request.POST.get('guard_travelling_allowance', quotation.guard_travelling_allowance)
        quotation.guard_house_duty = request.POST.get('guard_house_duty', quotation.guard_house_duty)
        quotation.guard_total_b = request.POST.get('guard_total_b', quotation.guard_total_b)
        quotation.guard_washing_allowance = request.POST.get('guard_washing_allowance', quotation.guard_washing_allowance)
        quotation.guard_hra = request.POST.get('guard_hra', quotation.guard_hra)
        quotation.guard_sub_total_c = request.POST.get('guard_sub_total_c', quotation.guard_sub_total_c)
        quotation.guard_pf = request.POST.get('guard_pf', quotation.guard_pf)
        quotation.guard_gratuity = request.POST.get('guard_gratuity', quotation.guard_gratuity)
        quotation.guard_leave_with_wages = request.POST.get('guard_leave_with_wages', quotation.guard_leave_with_wages)
        quotation.guard_esic = request.POST.get('guard_esic', quotation.guard_esic)
        quotation.guard_paid_holiday = request.POST.get('guard_paid_holiday', quotation.guard_paid_holiday)
        quotation.guard_bonus = request.POST.get('guard_bonus', quotation.guard_bonus)
        quotation.guard_uniform = request.POST.get('guard_uniform', quotation.guard_uniform)
        quotation.guard_total_c = request.POST.get('guard_total_c', quotation.guard_total_c)
        quotation.guard_service_charges = request.POST.get('guard_service_charges', quotation.guard_service_charges)
        quotation.guard_grand_total_per_month = request.POST.get('guard_grand_total_per_month', quotation.guard_grand_total_per_month)
        

        # Log updated state
        logger.info(f'Updated Quotation: {quotation}')

        # Generate a new PDF
        try:
            pdf_bytes = generate_quotation_pdf_security(quotation)
            pdf_file = ContentFile(pdf_bytes, name=f'{quotation.company}_updated.pdf')
            quotation.pdf_file.save(f'{quotation.company}_updated.pdf', pdf_file)
        except Exception as e:
            logger.error(f'Error generating PDF: {e}')
            return HttpResponse('Error generating PDF.', status=500)
        
        # Save the updated quotation
        try:
            quotation.save()
        except Exception as e:
            logger.error(f'Error saving quotation: {e}')
            return HttpResponse('Error saving quotation.', status=500)

        return HttpResponse('Quotation updated successfully!')

    return HttpResponse('Invalid request method.', status=405)
    




def generate_quotation_pdf_security(quotation):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%d-%m-%Y")


    # Paths to images
    top_image_path = finders.find('imgs/letter_top.png')  # Path to the top image
    bottom_image_path = finders.find('imgs/letter_end.png')  # Path to the bottom image

    if not top_image_path or not bottom_image_path:
        raise FileNotFoundError("One or both image files were not found.")

    # Image dimensions
    top_image_height = 100  # Adjust the height as needed
    bottom_image_height = 50  # Adjust the height as needed

    # Draw the top image
    p.drawImage(top_image_path, 0, height - top_image_height, width=width, height=top_image_height)

    # Draw the bottom image
    p.drawImage(bottom_image_path, 0, 0, width=width, height=bottom_image_height)

    # Define margins for content
    top_margin = top_image_height + 10  # Space below the top image
    bottom_margin = bottom_image_height + 10  # Space above the bottom image

    # Define available content height
    content_start_y = height - top_margin
    content_end_y = bottom_margin

    # Set the starting y position for text
    text_y_position = height - 140  # Adjust this value as needed

    p.saveState()
    watermark = finders.find('imgs/logo.png')
    p.setFillAlpha(0.15)  # Set transparency level
    p.drawImage(str(watermark), width / 4, height / 4, width=width / 2, height=height / 2, mask='auto')
    p.restoreState()
    
    # Add text
    p.drawString(100, text_y_position, f"To: {quotation.company}")
    
    data = [
        ['SR. No. 1', 'Particulars', 'Security Guard'],  # Header row
        ['1', 'Basic pay', quotation.guard_basic_pay],
        ['2', 'Special Allowance',quotation.guard_special_allowance ],
        ['3', 'Total (A)', quotation.guard_total_a],
        ['4', 'Conveyance Allowance', quotation.guard_conveyance_allowance],
        ['5', 'Education Allowance', quotation.guard_education_allowance],
        ['6', 'Travelling Allowance', quotation.guard_travelling_allowance],
        ['7', 'Hours Duty', quotation.guard_house_duty],
        ['8', 'Total (B)', quotation.guard_total_b],
        ['9', 'Washing Allowance', quotation.guard_washing_allowance],
        ['10', 'HRA @5% on (A)', quotation.guard_hra],
        ['11', 'Sub Total(c)', quotation.guard_sub_total_c],
        ['12', 'PF @13% on (A)',quotation.guard_pf],
        ['13', 'Gratuity', quotation.guard_gratuity],
        ['14', 'Leave with Wages @6% on C', quotation.guard_leave_with_wages],
        ['15', 'ESIC @3.25% on Sub Total (A)', quotation.guard_esic],
        ['16', 'Paid Holiday', quotation.guard_paid_holiday],
        ['17', 'Bonus/Ex-Gra @8.33% on (A)', quotation.guard_bonus],
        ['18', 'Uniform Charges', quotation.guard_uniform],
        ['19', 'Total (C)', quotation.guard_total_c],
        ['20', 'Service Charges', quotation.guard_service_charges],
        ['21', 'Grand Total per Month', quotation.guard_grand_total_per_month],
    ]

    # Create the table
    col_widths = [50, 225, 225,0]  # Example widths in points

    # Create the table with custom column widths
    table = Table(data, colWidths=col_widths, rowHeights=20)
    
    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alignment for all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Roman'),  # Font for header row
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Bottom padding for header row
        ('ROWHEIGHT', (0, 0), (-1, 0), 30),  # Set height for the header row
        ('BACKGROUND', (0, 1), (-1, -1), colors.transparent),  # Background color for data rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines for the entire table
    ]))


    # Calculate table position
    table_width, table_height = table.wrap(width, height)
    table_x = 50
    table_y = content_start_y - table_height - 60  # Adjust if needed

    # Draw the table on the canvas
    table.drawOn(p, table_x, table_y)


    gst_notice = "GST on Gross bill as per Government Notification"
    p.drawString(100, table_y - 20, gst_notice)

    # Add thank you note
    thank_you_note = "Thank you,"
    p.drawString(width - 100 - 100, bottom_margin + 90, thank_you_note)  # Align right
    company = "Best Security"
    p.drawString(width - 100 - 100, bottom_margin + 70, company) 
    p.drawString(width - 100 - 40, bottom_margin + 660, f"Date: {formatted_date}") 

    # Finalize the PDF
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    return pdf





##########Delete Quotation
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .models import Quotation

def delete_quotation(request, id):
    quotation = get_object_or_404(Quotation, id=id)
    
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You are not allowed to perform this action.")
    
    if request.method == 'POST':
        quotation.delete()
        return redirect('quotation_list')
    
    return HttpResponseForbidden("Invalid request method.")

############################################################

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader


def delete(request, id):
  member = quotation.objects.get(id=id)
  member.delete()
  return HttpResponseRedirect(reverse('quotation_list'))
###########################################


from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_quotation_pdf1(quotation):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%d-%m-%Y")


    # Paths to images
    top_image_path = finders.find('imgs/letter_top.png')  # Path to the top image
    bottom_image_path = finders.find('imgs/letter_end.png')  # Path to the bottom image

    if not top_image_path or not bottom_image_path:
        raise FileNotFoundError("One or both image files were not found.")

    # Image dimensions
    top_image_height = 100  # Adjust the height as needed
    bottom_image_height = 50  # Adjust the height as needed

    # Draw the top image
    p.drawImage(top_image_path, 0, height - top_image_height, width=width, height=top_image_height)

    # Draw the bottom image
    p.drawImage(bottom_image_path, 0, 0, width=width, height=bottom_image_height)

    # Define margins for content
    top_margin = top_image_height + 10  # Space below the top image
    bottom_margin = bottom_image_height + 10  # Space above the bottom image

    # Define available content height
    content_start_y = height - top_margin
    content_end_y = bottom_margin

    # Set the starting y position for text
    text_y_position = height - 140  # Adjust this value as needed

    p.saveState()
    watermark = finders.find('imgs/logo.png')
    p.setFillAlpha(0.15)  # Set transparency level
    p.drawImage(str(watermark), width / 4, height / 4, width=width / 2, height=height / 2, mask='auto')
    p.restoreState()
    
    # Add text
    p.drawString(100, text_y_position, f"To: {quotation.company}")
    
    data = [
        ['SR. No. 1', 'Particulars', 'Security Guard', 'Supervisor'],  # Header row
        ['1', 'Basic pay', quotation.guard_basic_pay, quotation.supervisor_basic_pay],
        ['2', 'Special Allowance',quotation.guard_special_allowance , quotation.supervisor_special_allowance],
        ['3', 'Total (A)', quotation.guard_total_a,quotation.supervisor_total_a],
        ['4', 'Conveyance Allowance', quotation.guard_conveyance_allowance,quotation.supervisor_conveyance_allowance],
        ['5', 'Education Allowance', quotation.guard_education_allowance,quotation.supervisor_education_allowance],
        ['6', 'Travelling Allowance', quotation.guard_travelling_allowance,quotation.supervisor_travelling_allowance],
        ['7', 'Hours Duty', quotation.guard_house_duty, quotation.supervisor_house_duty],
        ['8', 'Total (B)', quotation.guard_total_b, quotation.supervisor_total_b],
        ['9', 'Washing Allowance', quotation.guard_washing_allowance, quotation.supervisor_washing_allowance],
        ['10', 'HRA @5% on (A)', quotation.guard_hra,quotation.supervisor_hra],
        ['11', 'Sub Total(c)', quotation.guard_sub_total_c,quotation.supervisor_sub_total_c],
        ['12', 'PF @13% on (A)',quotation.guard_pf, quotation.supervisor_pf],
        ['13', 'Gratuity', quotation.guard_gratuity, quotation.supervisor_gratuity],
        ['14', 'Leave with Wages @6% on C', quotation.guard_leave_with_wages, quotation.supervisor_leave_with_wages],
        ['15', 'ESIC @3.25% on Sub Total (A)', quotation.guard_esic, quotation.supervisor_esic],
        ['16', 'Paid Holiday', quotation.guard_paid_holiday, quotation.supervisor_paid_holiday],
        ['17', 'Bonus/Ex-Gra @8.33% on (A)', quotation.guard_bonus,quotation.supervisor_bonus],
        ['18', 'Uniform Charges', quotation.guard_uniform, quotation.supervisor_uniform],
        ['19', 'Total (C)', quotation.guard_total_c, quotation.supervisor_total_c],
        ['20', 'Service Charges', quotation.guard_service_charges, quotation.supervisor_service_charges],
        ['21', 'Grand Total per Month', quotation.guard_grand_total_per_month, quotation.supervisor_grand_total_per_month],
    ]

    # Create the table
    col_widths = [50, 200, 125, 125]  # Example widths in points

    # Create the table with custom column widths
    table = Table(data, colWidths=col_widths, rowHeights=20)
    
    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alignment for all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Roman'),  # Font for header row
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Bottom padding for header row
        ('ROWHEIGHT', (0, 0), (-1, 0), 30),  # Set height for the header row
        ('BACKGROUND', (0, 1), (-1, -1), colors.transparent),  # Background color for data rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines for the entire table
    ]))


    # Calculate table position
    table_width, table_height = table.wrap(width, height)
    table_x = 50
    table_y = content_start_y - table_height - 60  # Adjust if needed

    # Draw the table on the canvas
    table.drawOn(p, table_x, table_y)


    gst_notice = "GST on Gross bill as per Government Notification"
    p.drawString(100, table_y - 20, gst_notice)
    text1 = "The above quotation is for 30/31 Days (12 Hours ) only."
    p.drawString(100, table_y - 40, text1)
    # Add thank you note
    thank_you_note = "Thank you,"
    p.drawString(width - 100 - 100, bottom_margin + 90, thank_you_note)  # Align right
    company = "Best Security"
    p.drawString(width - 100 - 100, bottom_margin + 70, company) 
    p.drawString(width - 100 - 40, bottom_margin + 660, f"Date: {formatted_date}") 

    # Finalize the PDF
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    return pdf




from django.shortcuts import render, get_object_or_404
from .models import UserProfile, EmployeeJoining


@role_required('fo')
def company_list(request):
    companies = UserProfile.objects.filter(user_type='company')
    
    company_data = []
    for company in companies:
        guard_count = EmployeeJoining.objects.filter(company=company, position='Security Guard').count()
        supervisor_count = EmployeeJoining.objects.filter(company=company, position='Supervisor').count()
        print(f"Company ID: {company.id}, Guards: {guard_count}, Supervisors: {supervisor_count}")  # Debugging line
        company_data.append({
            'company': company,
            'guard_count': guard_count,
            'supervisor_count': supervisor_count
        })
    
    return render(request, 'FO/company_list.html', {'company_data': company_data})


def company_employees(request, company_id):
    company = get_object_or_404(UserProfile, id=company_id, user_type='company')
    guards = EmployeeJoining.objects.filter(company=company, position='Security Guard')
    supervisors = EmployeeJoining.objects.filter(company=company, position='Supervisor')
    return render(request, 'FO/company_employees.html', {
        'company': company,
        'guards': guards,
        'supervisors': supervisors
    })



from django.shortcuts import redirect
from .models import UserProfile, EmployeeJoining
from django.http import HttpResponse

from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from .models import UserProfile, TaxInvoice
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from django.conf import settings

from django.core.files.base import ContentFile
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import TaxInvoice
  # Adjust import as needed


import uuid

def generate_unique_invoice_number(company_id):
    # Get the last invoice number for the given company
    last_invoice = TaxInvoice.objects.filter(invoice_number__startswith='BSS').order_by('-invoice_number').first()

    # Determine the next invoice number
    if last_invoice:
        last_number = int(last_invoice.invoice_number[3:])  # Extract the number part
        next_number = last_number + 1
    else:
        next_number = 1

    # Format the next number with leading zeros
    next_invoice_number = f"BSS{str(next_number).zfill(3)}"

    return next_invoice_number


@role_required('fo')
def create_tax_invoice(request):
    if request.method == 'POST':
        company_id = request.POST['company_id']
        po = request.POST.get('po')
        invoice_number = request.POST.get('invoice_number')  # Correct key here
        month = request.POST['month']
        year = request.POST['year']
        guard_count = request.POST['guard_count']
        amount_per_guard = request.POST['amount_per_guard']
        supervisor_count = request.POST.get('supervisor_count', 0)
        amount_per_supervisor = request.POST.get('amount_per_supervisor', 0)
        sub_total = request.POST.get('sub_total')
        cgst = request.POST.get('cgst')
        sgst = request.POST.get('sgst')
        total_amount = request.POST.get('total_amount')

        # Ensure the invoice number is provided
        if not invoice_number:
            return HttpResponse("Invoice number is required.", status=400)

        # Get the company instance
        company = UserProfile.objects.get(id=company_id)

        # Generate the PDF with the invoice number included
        pdf_data = generate_tax_invoice_pdf(
            company, month, year, po, invoice_number, guard_count,
            amount_per_guard, supervisor_count, amount_per_supervisor,
            total_amount, sub_total, cgst, sgst
        )

        # Create a TaxInvoice object
        tax_invoice = TaxInvoice(
            company=company,
            month=month,
            year=year,
            po=po,
            invoice_number=invoice_number,  # Use the user-provided invoice number
            guard_count=guard_count,
            amount_per_guard=amount_per_guard,
            supervisor_count=supervisor_count,
            amount_per_supervisor=amount_per_supervisor,
            total_amount=total_amount,
            sub_total=sub_total,
            cgst=cgst,
            sgst=sgst,
        )

        # Save the TaxInvoice object before saving the PDF file
        tax_invoice.save()

        # Save the PDF to the FileField using ContentFile
        pdf_file_name = f"invoice_{invoice_number}.pdf"
        tax_invoice.pdf_file.save(pdf_file_name, ContentFile(pdf_data))
        
        # Serve the PDF file as a download
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_file_name}"'
        return response

    return redirect('FO/company_list')



def number_to_words(number):
    p = inflect.engine()
    
    try:
        # Convert input to float and handle invalid values
        number = float(number)
        
        # Separate the integer and decimal parts
        rupees = int(number)
        paise = round((number - rupees) * 100)

        # Convert the integer and decimal parts to words
        rupees_words = p.number_to_words(rupees, andword=", and")
        if paise > 0:
            paise_words = p.number_to_words(paise, andword=", and")
            amount_words = f"{rupees_words} rupees and {paise_words} paise"
        else:
            amount_words = f"{rupees_words} rupees"
        
        # Capitalize the first letter and add "ONLY" at the end
        amount_words = amount_words.capitalize() + " only"
        
        return amount_words

    except ValueError:
        # Handle cases where the input is not a valid number
        return "Invalid amount"




from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.core.files.base import ContentFile
from django.core.files import File
from datetime import datetime


def generate_tax_invoice_pdf(company, month, year, guard_count,po, amount_per_guard, supervisor_count, amount_per_supervisor, total_amount, sub_total, cgst, sgst, invoice_number):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    cur_date = datetime.now().date()
    format_date = cur_date.strftime("%d-%m-%Y")

    # Paths to images
    top_image_path = finders.find('imgs/letter_top.png')  # Path to the top image
    bottom_image_path = finders.find('imgs/letter_end.png')  # Path to the bottom image
      # Path to the watermark image

    # Image dimensions
    top_image_height = 100  # Height of the top image
    bottom_image_height = 50  # Height of the bottom image

    # Draw the top image
    p.drawImage(str(top_image_path), 0, height - top_image_height, width=width, height=top_image_height)

    # Draw the bottom image
    p.drawImage(str(bottom_image_path), 0, 0, width=width, height=bottom_image_height)

    p.saveState()
    watermark = finders.find('imgs/logo.png')
    p.setFillAlpha(0.15)  # Set transparency level
    p.drawImage(str(watermark), width / 4, height / 4, width=width / 2, height=height / 2, mask='auto')
    p.restoreState()

    # Define margins for content
    top_margin = top_image_height + 10  # Space below the top image
    bottom_margin = bottom_image_height + 10  # Space above the bottom image

    # Set up the document
    title_y_position = height - top_margin - 40
    p.setFont("Times-Roman", 14)
    p.drawCentredString(width / 2, title_y_position, "Tax Invoice")

    # First table (2 columns, 1 row, no header)
    first_table_data = [
        [f"Invoice Number:{invoice_number}", f"Date: {format_date}"],  # Example data
    ]
    
    first_table = Table(first_table_data, colWidths=[200, 250], rowHeights=20)
    first_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.transparent),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'), 
    ]))
    
    first_table_width, first_table_height = first_table.wrap(width, height)
    first_table_x = (width - first_table_width) / 2
    first_table_y = title_y_position - 50  # Position the table below the title

    # Draw the first table on the canvas
    first_table.drawOn(p, first_table_x, first_table_y)


    company_to_send = (
        f"To,\n"
        f"{company.user.first_name}\n"
        f"\n"
        f"{company.user.last_name}\n"
        f"\n"
        f"GST No. : {company.gst_or_emergency}\n"
    )
    # Second table (3 columns, 1 row, no header, increased row height)
    second_table_data = [
        [company_to_send, f"Po Number:{po}", ""],  # Example data
    ]
    
    second_table = Table(second_table_data, colWidths=[300, 0, 150], rowHeights=80)
    second_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content to the top
        ('BACKGROUND', (0, 0), (-1, -1), colors.transparent),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'), 
    ]))

    
    second_table_width, second_table_height = second_table.wrap(width, height)
    second_table_x = (width - second_table_width) / 2
    second_table_y = first_table_y - second_table_height  # No additional space, directly attached to the first table

    # Draw the second table on the canvas
    second_table.drawOn(p, second_table_x, second_table_y)

    # Third table (2 columns, 1 row, no header)
    third_table_data = [
        ["Service Details", "Amount"],  # Example data
    ]
    
    third_table = Table(third_table_data, colWidths=[350, 100], rowHeights=20)
    third_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.transparent),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
    ]))
    
    third_table_width, third_table_height = third_table.wrap(width, height)
    third_table_x = (width - third_table_width) / 2
    third_table_y = second_table_y - third_table_height  # Directly attached to the second table

    # Draw the third table on the canvas
    third_table.drawOn(p, third_table_x, third_table_y)
    styles = getSampleStyleSheet()
    services = (
        f"For Security Services provided during the month of {month}-{year}\n"
        f"\n"
        f"\n"
        f"\n"
        f"Security Guard: -{guard_count}\n"
        f"Supervisor: -{supervisor_count}\n"
        f"\n"
        f"\n"
        f"Our\n"
        f"Company Name : Best Security Services\n"
        f"Pan No. : AOQPJ1060H\n"
        f"GST No. : 27AOQPJ1060H1ZX\n"
    )

    service_amount = (
        f"\n"
        f"\n"
        f"\n"
        f"\n"
        f"{amount_per_guard}.00\n"
        f"{amount_per_supervisor}.00\n"
        f"\n"
        f"\n"
        f"\n"
        f"\n"
        f"\n"
        f"\n"
    )
    



    # Fourth table (7 rows, 2 columns, no header, increased height for first row)
    fourth_table_data = [
        [services,service_amount],  # Example data for the first row
        ["SUBTOTAL",sub_total],
        ["CGST", cgst],
        ["SGST", sgst],
        ["", ""],
        ["TOTAL DUE", total_amount],
        [f"Total in Words: {number_to_words(total_amount)}","" ],
    ]
    
    row_heights = [150] + [15] * 6  # First row has more height (50), others have 30
    fourth_table = Table(fourth_table_data, colWidths=[350, 100], rowHeights=row_heights)
    fourth_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, 0), 'LEFT'),  # Align first row to the left
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (1, 0), 'TOP'),  # Align first row content to the top
        ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),  # Align all other rows to the right
        ('BACKGROUND', (0, 0), (-1, -1), colors.transparent),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'), 
    ]))
    fourth_table_width, fourth_table_height = fourth_table.wrap(width, height)
    fourth_table_x = (width - fourth_table_width) / 2
    fourth_table_y = third_table_y - fourth_table_height  # Directly attached to the third table

    # Draw the fourth table on the canvas
    fourth_table.drawOn(p, fourth_table_x, fourth_table_y)



    terms = (
    "Payment Terms\n"
    "       •   Interest @24% P.A. will be charged if the bill is not paid before the due date as per contract.\n"
    "       •   Kindly pay by cheque/demand draft in favour of Best Security Services.\n"
    "       •   For prompt updation of payment, an advice with details is a must.\n"
    "       •   Prompt issue of TDS certificate will be appreciated.\n"
    "       •   Cash payment only on Company's written authority."
)

    # Fifth table (1 row, 1 column, transparent background)
    fifth_table_data = [
        [terms],  # Example data
    ]
    fifth_table = Table(fifth_table_data, colWidths=[450], rowHeights=100)
    fifth_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (1, 0), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.transparent),  # Transparent background
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'), 
    ]))
    
    fifth_table_width, fifth_table_height = fifth_table.wrap(width, height)
    fifth_table_x = (width - fifth_table_width) / 2
    fifth_table_y = fourth_table_y - fifth_table_height  # Directly attached to the fourth table

    # Draw the fifth table on the canvas
    fifth_table.drawOn(p, fifth_table_x, fifth_table_y)

    signature_x_position = width - 150  # Adjust the horizontal position as needed
    signature_y_position = fifth_table_y - 50  # Adjust the vertical position as needed

    p.setFont("Times-Roman", 12)
    p.line(signature_x_position, signature_y_position - 10, signature_x_position + 100, signature_y_position - 10)  # Line for signature
    p.drawString(signature_x_position, signature_y_position - 30, "Authorised Signature")
    

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    return pdf



############################## Salary Sheet ###########################################







from datetime import datetime
from django.shortcuts import render
from .models import SalaryDetails, Attendance

def calculate_actual_daily_wages(total_c, days_in_month):
    if days_in_month > 0:
        return total_c / days_in_month
    else:
        return 0

def calculate_actual_salary(actual_daily_wages, days_present):
    return actual_daily_wages * days_present

from django.shortcuts import render
from datetime import datetime
from decimal import Decimal
from .models import SalaryDetails, Attendance, AdvancePayment


@role_required('fo')
def salarysheet(request):
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # Get the number of days in the current month
    days_in_month = (datetime(current_year, current_month + 1, 1) - datetime(current_year, current_month, 1)).days

    # Get all salary details
    salary_details_list = SalaryDetails.objects.all()
    advance_payments = AdvancePayment.objects.all()

    # Create a dictionary to hold total advance payments per employee
    advance_amounts = {}
    for advance in advance_payments:
        if advance.employee.id in advance_amounts:
            advance_amounts[advance.employee.id] += advance.advance_amount
        else:
            advance_amounts[advance.employee.id] = advance.advance_amount

    # Create a list to hold salary details with actual salary
    salary_with_actual = []

    for salary in salary_details_list:
        # Calculate number of days present in the current month
        days_present = Attendance.objects.filter(
            employee=salary.employee,
            date__month=current_month,
            date__year=current_year,
            status='P'  # Adjust 'Present' to whatever value represents attendance
        ).count()

        # Calculate the actual daily wages
        actual_daily_wages = calculate_actual_daily_wages(Decimal(salary.total_c), days_in_month)

        # Calculate the actual salary
        total_advance_amount = Decimal(advance_amounts.get(salary.employee.id, 0))
        actual_salary = calculate_actual_salary(actual_daily_wages, days_present) - total_advance_amount - Decimal(salary.food_allowance) - Decimal(salary.price_partial_uniform)

        salary_with_actual.append({
            'employee': salary.employee,
            'basic_salary': salary.basic_salary,
            'special_allowance': salary.special_allowance,
            'total': salary.total,
            'conveyance_allowance': salary.conveyance_allowance,
            'education_allowance': salary.education_allowance,
            'travelling_allowance': salary.travelling_allowance,
            'hours_daily_duty': salary.hours_daily_duty,
            'total_b': salary.total_b,
            'hra': salary.hra,
            'pf': salary.pf,
            'gratuity': salary.gratuity,
            'leave_with_wages': salary.leave_with_wages,
            'esic': salary.esic,
            'paid_holiday': salary.paid_holiday,
            'bonus': salary.bonus,
            'uniform': salary.uniform,
            'total_c': salary.total_c,
            'advance_amount': total_advance_amount,
            'food_allowance': Decimal(salary.food_allowance),
            'price_partial_uniform': Decimal(salary.price_partial_uniform),
            'actual_daily_wages': actual_daily_wages,
            'actual_salary': actual_salary,
        })

    return render(request, 'FO/salarysheet.html', {'salary_with_actual': salary_with_actual})






@role_required('fo')
def present(request):
    companies = UserProfile.objects.filter(user_type='company')
    return render(request, 'FO/present.html', {'companies': companies})

def get_employees(request):
    company_id = request.GET.get('company_id')
    employees = EmployeeJoining.objects.filter(company_id=company_id).values('emp_id', 'first_name', 'last_name')
    employees_list = list(employees)
    return JsonResponse(employees_list, safe=False)



# views.py


@role_required('fo')
def monthly_attendance(request, emp_id):
    employee = get_object_or_404(EmployeeJoining, emp_id=emp_id)
    
    # Get the current year and month or use provided query parameters
    now = datetime.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    # Filter attendance records by the selected month and year
    attendance_records = Attendance.objects.filter(employee_id=employee.id, date__year=year, date__month=month)

    # Create a list of months for the dropdown
    months = [(i, datetime.strptime(str(i), '%m').strftime('%B')) for i in range(1, 13)]

    return render(request, 'FO/monthlyattendance.html', {
        'employee': employee,
        'attendance_records': attendance_records,
        'year': year,
        'month': month,
        'months': months,
    })
    
    
from django.contrib import messages



@role_required('fo')
def mess_view(request, emp_id):
    salary_detail = get_object_or_404(SalaryDetails, employee__emp_id=emp_id)
    
    if request.method == 'POST':
        new_food_allowance = request.POST.get('food_allowance')
        salary_detail.food_allowance = new_food_allowance
        salary_detail.save()
        return redirect(reverse('mess', args=[emp_id]))

    context = {
        'salary_detail': salary_detail,
        'employee': salary_detail.employee,
    }
    return render(request, 'FO/mess.html', context)

@role_required('fo')
def partial_uniform_view(request, emp_id):
    salary_detail = get_object_or_404(SalaryDetails, employee__emp_id=emp_id)
    employees = EmployeeJoining.objects.get(emp_id=emp_id)
    
    if request.method == 'POST':
        uniform_status = request.POST.get('partialuniform')
        employees.partialuniform = uniform_status
        new_price_partial_uniform = request.POST.get('price_partial_uniform')
        salary_detail.price_partial_uniform = new_price_partial_uniform
        salary_detail.save()
        employees.save()
        return redirect(reverse('partial_uniform', args=[emp_id]))

    context = {
        'salary_detail': salary_detail,
        'employees':employees,
        'employee': salary_detail.employee,
    }
    return render(request, 'FO/partial_uniform.html', context)



def adminsalarysheet(request):
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year

    next_month = current_date.replace(day=28) + timezone.timedelta(days=4)
    first_day_next_month = next_month.replace(day=1)
    days_in_month = (first_day_next_month - current_date.replace(day=1)).days

    salary_details_list = SalaryDetails.objects.all()

    salary_with_actual = []

    for salary in salary_details_list:
        days_present = Attendance.objects.filter(
            employee=salary.employee,
            date__month=current_month,
            date__year=current_year,
            status='P'
        ).count()

        actual_daily_wages = calculate_actual_daily_wages(salary.total_c, days_in_month) if days_in_month else 0
        actual_salary = calculate_actual_salary(actual_daily_wages, days_present) - salary.advance_payment - salary.food_allowance - salary.price_partial_uniform

        salary_with_actual.append({
            'id': salary.id,
            'employee': salary.employee.first_name,  # Assuming Employee has a 'name' field
            'basic_salary': salary.basic_salary,
            'special_allowance': salary.special_allowance,
            'total': salary.total,
            'conveyance_allowance': salary.conveyance_allowance,
            'education_allowance': salary.education_allowance,
            'travelling_allowance': salary.travelling_allowance,
            'hours_daily_duty': salary.hours_daily_duty,
            'total_b': salary.total_b,
            'hra': salary.hra,
            'pf': salary.pf,
            'gratuity': salary.gratuity,
            'leave_with_wages': salary.leave_with_wages,
            'esic': salary.esic,
            'paid_holiday': salary.paid_holiday,
            'bonus': salary.bonus,
            'uniform': salary.uniform,
            'total_c': salary.total_c,
            'service_charge': salary.service_charge,
            'advance_payment': salary.advance_payment,
            'food_allowance': salary.food_allowance,
            'price_partial_uniform': salary.price_partial_uniform,
            'actual_daily_wages': actual_daily_wages,
            'actual_salary': actual_salary,
        })

    return render(request, 'admin/adsalarysheet.html', {'salary_with_actual': salary_with_actual})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import SalaryDetails

@csrf_exempt
@require_POST
def update_salary(request):
    try:
        data = json.loads(request.body)
        salary_id = data.get('id')

        if not salary_id:
            return JsonResponse({'error': 'ID is required'}, status=400)

        salary = SalaryDetails.objects.get(id=salary_id)
        salary.basic_salary = data.get('basic_salary', salary.basic_salary)
        salary.special_allowance = data.get('special_allowance', salary.special_allowance)
        salary.total = data.get('total', salary.total)
        salary.conveyance_allowance = data.get('conveyance_allowance', salary.conveyance_allowance)
        salary.education_allowance = data.get('education_allowance', salary.education_allowance)
        salary.travelling_allowance = data.get('travelling_allowance', salary.travelling_allowance)
        salary.hours_daily_duty = data.get('hours_daily_duty', salary.hours_daily_duty)
        salary.total_b = data.get('total_b', salary.total_b)
        salary.hra = data.get('hra', salary.hra)
        salary.pf = data.get('pf', salary.pf)
        salary.gratuity = data.get('gratuity', salary.gratuity)
        salary.leave_with_wages = data.get('leave_with_wages', salary.leave_with_wages)
        salary.esic = data.get('esic', salary.esic)
        salary.paid_holiday = data.get('paid_holiday', salary.paid_holiday)
        salary.bonus = data.get('bonus', salary.bonus)
        salary.uniform = data.get('uniform', salary.uniform)
        salary.advance_payment = data.get('advance_payment', salary.advance_payment)
        salary.food_allowance = data.get('food_allowance', salary.food_allowance)
        salary.price_partial_uniform = data.get('price_partial_uniform', salary.price_partial_uniform)
        salary.total_c = data.get('total_c', salary.total_c)
        salary.actual_salary = data.get('actual_salary', salary.actual_salary)

        salary.save()

        return JsonResponse({'success': True})
    except SalaryDetails.DoesNotExist:
        return JsonResponse({'error': 'SalaryDetails not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import EmployeeJoining, SalaryDetails

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import EmployeeJoining, SalaryDetails

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import EmployeeJoining, SalaryDetails, AdvancePayment


@role_required('fo')
def advance(request, employee_id):
    # Fetch employee and salary details
    employee = get_object_or_404(EmployeeJoining, emp_id=employee_id)
    salary_details = get_object_or_404(SalaryDetails, employee=employee)

    # Handle the form submission for advance payment request
    if request.method == 'POST':
        # Check if an advance payment request is already pending or processed
        if not AdvancePayment.objects.filter(employee=employee, request_status='Pending').exists():
            advance_amount = request.POST.get('advance_amount')
            receipt_number = request.POST.get('receipt_number')
            reason = request.POST.get('reason')

            # Create a new advance payment request
            advance_payment = AdvancePayment.objects.create(
                employee=employee,
                salary_details=salary_details,
                receipt_number = receipt_number,
                advance_amount=advance_amount,
                reason = reason,
                request_status='Pending',  # Mark the request as pending
                request_date=timezone.now(),
            )

            # Save the advance payment
            advance_payment.save()

            # Notify the user/admin (can be email, dashboard notification, etc.)
            messages.success(request, 'Advance payment request submitted successfully. Waiting for admin approval.')
        else:
            messages.error(request, 'An advance payment request is already pending for this employee.')

        return redirect('present')

    # Render the advance form
    return render(request, 'FO/advance.html', {
        'employee': employee,
        'salary_details': salary_details
    })




from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from .models import AdvancePayment


@role_required('superuser')
def advance_requests(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_requests = request.POST.getlist('selected_requests')

        if action == 'approve':
            # Approve selected advance requests
            AdvancePayment.objects.filter(pk__in=selected_requests).update(
                request_status='Approved',
                approval_date=timezone.now()
            )
            messages.success(request, 'Selected advance payment requests approved.')
        elif action == 'reject':
            # Reject selected advance requests
            AdvancePayment.objects.filter(pk__in=selected_requests).update(
                request_status='Rejected',
                approval_date=timezone.now()
            )
            messages.success(request, 'Selected advance payment requests rejected.')
        else:
            messages.error(request, 'Invalid action.')

        return redirect('advance_requests')

    # Fetch all pending advance payment requests
    requests = AdvancePayment.objects.filter(request_status='Pending')
    return render(request, 'admin/advance_requests.html', {'requests': requests})



from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import AdvancePayment

import os



def approve_advance(request, pk):
    advance_payment = get_object_or_404(AdvancePayment, pk=pk)
    
    if request.method == 'POST':
        advance_payment.request_status = 'Approved'
        advance_payment.approval_date = timezone.now()
        advance_payment.save()

        # Generate PDF
        pdf_buffer = generate_approval_pdf(
            employee_id=advance_payment.employee.id,
            name=advance_payment.employee.first_name + " " + 
                 advance_payment.employee.middle_name + " " + 
                 advance_payment.employee.last_name,
            amount_approved=advance_payment.advance_amount,
            receipt_number=advance_payment.receipt_number,
            reason=advance_payment.reason,
        )

        # Define PDF path
        pdf_filename = f'advance_payment_{pk}.pdf'
        pdf_dir = os.path.join('media', 'advance_pdfs')
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        # Ensure directory exists
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)  # Create the directory if it doesn't exist

        # Save the PDF to the file system
        with open(pdf_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        # Update the model to store the path of the generated PDF
        advance_payment.approval_pdf = os.path.join('advance_pdfs', pdf_filename)
        advance_payment.save()

        # Prepare the response to download the PDF
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'

        messages.success(request, 'Advance payment approved and PDF generated.')
        return response
    
    else:
        messages.error(request, 'Invalid request method.')
    
    return redirect('advance_requests')


def generate_approval_pdf(employee_id, name, amount_approved, receipt_number, reason):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%d-%m-%Y")

    # Paths to images
    top_image_path = finders.find('imgs/letter_top.png')  # Path to the top image
    bottom_image_path = finders.find('imgs/letter_end.png')  # Path to the bottom image
    watermark_image_path = finders.find('imgs/logo.png')  # Path to the watermark image (optional)

    if not top_image_path or not bottom_image_path:
        raise FileNotFoundError("One or both image files were not found.")

    # Image dimensions
    top_image_height = 120  # Top image height
    bottom_image_height = 60  # Bottom image height

    # Draw the top image (logo/header)
    p.drawImage(top_image_path, 0, height - top_image_height, width=width, height=top_image_height)

    # Draw the bottom image (footer)
    p.drawImage(bottom_image_path, 0, 0, width=width, height=bottom_image_height)

    # Add watermark (Optional: Image or Text)
    if watermark_image_path:
        watermark_width = 300
        watermark_height = 300
        p.setFillAlpha(0.1)  # Set transparency to make it look like a watermark
        p.drawImage(watermark_image_path, (width - watermark_width) / 2, (height - watermark_height) / 2, 
                    width=watermark_width, height=watermark_height, mask='auto')
    else:
        p.setFont("Helvetica-Bold", 50)
        p.setFillColorRGB(0.5, 0.5, 0.5)  # Light gray color for the watermark
        p.setFillAlpha(0.1)  # Set transparency
        text = "CONFIDENTIAL"
        text_width = p.stringWidth(text, "Helvetica-Bold", 50)
        p.drawString((width - text_width) / 2, height / 2, text)

    # Reset transparency after watermark
    p.setFillAlpha(1)

    # Define margins for content
    top_margin = top_image_height + 20  # Space below the top image
    bottom_margin = bottom_image_height + 20  # Space above the bottom image

    # Adjust content height
    content_height = height - top_margin - bottom_margin - 50  # Reduced content height

    # Define available content height
    content_start_y = height - top_margin
    content_end_y = bottom_margin + content_height

    # Add content to PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, content_start_y - 40, "Advance Payment Receipt")
    p.setFont("Helvetica", 12)
    p.drawString(60, content_start_y - 60, f"Receipt Number: {receipt_number}")

    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)

    # Add the grid table
    table_data = [
        ["", ""],
        ["Employee ID:", employee_id],
        ["Employee Name:", name],
        ["Reason:", reason],
        ["Amount Approved:", f"Rs. {amount_approved:,.2f}"]
    ]
    
    row_heights = [00, 30, 30, 30, 30]  # Custom heights for each row

    # Create the table with custom row heights
    table = Table(table_data, colWidths=[2*inch, 4*inch], rowHeights=row_heights)

    # Set the table style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ]))

    # Wrap and position the table as before
    table_width, table_height = table.wrapOn(p, width - 2 * inch, content_height - 60)
    table_x = (width - table_width) / 2
    table_y = content_start_y - table_height - 100

    table.drawOn(p, table_x, table_y)

    # Add thank you note
   
    p.setFont("Helvetica", 12)
    p.drawString(425, bottom_margin + 280, "Best Regards,")
    p.drawString(425, bottom_margin + 260, "Best Security")

    # Add date
    p.setFont("Helvetica", 10)
    p.drawString(425, content_start_y - 20, f"Date: {formatted_date}")
    p.drawString(60, content_start_y + 220, "This is Computer generated receipt therfore signature is not required")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer






def reject_advance(request, pk):
    advance_payment = get_object_or_404(AdvancePayment, pk=pk)
    if request.method == 'POST':
        advance_payment.request_status = 'Rejected'
        advance_payment.approval_date = timezone.now()
        advance_payment.save()
        messages.success(request, 'Advance payment rejected.')
        return redirect('advance_requests')
    else:
        return redirect('advance_requests')






# views.py
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import AdvancePayment


@role_required('fo')
def approved_requests(request):
    # Fetch all approved advance payments
    approved_payments = AdvancePayment.objects.filter(request_status='Approved')
    
    # Pagination
    paginator = Paginator(approved_payments, 10)  # Show 10 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, 'FO/approved_requests.html', context)

# views.py
from django.http import HttpResponse, Http404
from django.conf import settings
import os

def view_pdf(request, pk):
    try:
        advance_payment = AdvancePayment.objects.get(pk=pk)
        pdf_file = advance_payment.approval_pdf
        
        if pdf_file:
            # Construct the absolute path to the PDF file
            pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)

            # Debug: print the constructed path to ensure it's correct
            print("PDF path:", pdf_path)

            if not os.path.exists(pdf_path):
                raise Http404("PDF not found.")
            
            with open(pdf_path, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
                return response
        else:
            raise Http404("No PDF available for this request.")
    except AdvancePayment.DoesNotExist:
        raise Http404("Advance payment not found.")


from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

def add_page_elements(canvas, doc, header_image_path, footer_image_path, watermark_image_path):
    width, height = letter

    # Draw header image (adjust width to page width)
    header_img = Image(header_image_path, width=width, height=100)  # Adjust height as needed
    header_img.drawOn(canvas, 0, height - 100)

    # Draw footer image (adjust width to page width)
    footer_img = Image(footer_image_path, width=width, height=60)  # Adjust height as needed
    footer_img.drawOn(canvas, 0, 10)

    # Draw watermark in the center of the page with transparency
    watermark_img = Image(watermark_image_path, width=300, height=300)  # Adjust size as needed
    watermark_x = (width - 300) / 2  # Center horizontally
    watermark_y = (height - 300) / 2  # Center vertically

    # Draw the watermark image on the canvas
    canvas.saveState()  # Save the current state of the canvas
    canvas.setFillAlpha(0.3)  # Set transparency (0.0 to 1.0)
    canvas.drawImage(watermark_image_path, watermark_x, watermark_y, width=300, height=300, mask='auto')
    canvas.restoreState()  # Restore the canvas to its original state

def pdf_generate(request, salary_id):
    # Fetch the salary details and employee information
    try:
        salary_details = SalaryDetails.objects.get(id=salary_id)
        employee = salary_details.employee
    except SalaryDetails.DoesNotExist:
        return HttpResponse("Salary details not found.", status=404)

    # Create a buffer to store PDF content
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Prepare dynamic values
    title = ""
    salary_month_year = "September 2024"  # Adjust as needed
    employee_name = f"{employee.first_name} {employee.last_name}"
    employee_id = employee.emp_id
    designation = employee.position
    uan_number = "1234567890"  # Update with actual UAN if available
    aadhaar_number = employee.aadhar  # Update with actual Aadhaar if available
    pan_card_number = employee.pancard  # Update with actual PAN if available
    bank_name = employee.bank_name
    account_number = employee.bank_account_number
    dob = employee.date_of_birth.strftime('%Y-%m-%d')
    company_name = "Company ABC"  # Update as needed

    # Paths to images
    header_image_path = finders.find('imgs/letter_top.png')
    footer_image_path = finders.find('imgs/letter_end.png')
    watermark_image_path = finders.find('imgs/logo.png')

    # Create a list to hold the PDF elements
    story = []

    story.append(Spacer(1, 50)) 

    # Title for the PDF
    story.append(Paragraph(title, styles['Title']))
    story.append(Paragraph(f"SALARY SLIP FOR THE MONTH OF - {salary_month_year}", styles['Title']))

    # Prepare data for the first table (Employee Information)
    table_data_employee = [
        [f'Salary for {salary_month_year}', '', 'Employee ID', employee_id],
        [Paragraph('<b>Employee Name:</b>', styles['Normal']), Paragraph(employee_name, styles['Normal']),
         Paragraph('<b>Designation:</b>', styles['Normal']), Paragraph(designation, styles['Normal'])],
        [Paragraph('<b>Date of Joining:</b>', styles['Normal']), Paragraph("joining_date", styles['Normal']),
         Paragraph('<b>Date of Probation:</b>', styles['Normal']), Paragraph("probation_date", styles['Normal'])],
        [Paragraph('<b>UAN Number:</b>', styles['Normal']), Paragraph(uan_number, styles['Normal']),
         Paragraph('<b>Aadhaar Number:</b>', styles['Normal']), Paragraph(aadhaar_number, styles['Normal'])],
        [Paragraph('<b>PAN Card Number:</b>', styles['Normal']), Paragraph(pan_card_number, styles['Normal']),
         Paragraph('<b>Bank Name:</b>', styles['Normal']), Paragraph(bank_name, styles['Normal'])],
        [Paragraph('<b>Account Number:</b>', styles['Normal']), Paragraph(account_number, styles['Normal']),
         Paragraph('<b>Date of Birth:</b>', styles['Normal']), Paragraph(dob, styles['Normal'])],
        [Paragraph('<b>Company Name:</b>', styles['Normal']), Paragraph(company_name, styles['Normal']), '', '']
    ]

    # Create a table for Employee Information and style
    table_employee = Table(table_data_employee, colWidths=[150, 150, 150, 150], repeatRows=1, hAlign='CENTER')
    table_employee.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ]))

    # Add Employee Information table to the story
    story.append(table_employee)

    

    # Prepare data for the second table (Attendance and Leave Details)
    # Replace with actual data if needed
    

    # Create the additional row with 2 columns spanning the entire table width
    additional_row_data = [
        [Paragraph('<b>Earnings</b>', styles['Normal']), Paragraph('<b>Deductions</b>', styles['Normal'])]
    ]

    # Create a table for the additional row and style
    additional_row = Table(additional_row_data, colWidths=[300, 300], hAlign='CENTER')
    additional_row.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    # Add the additional row to the story
    story.append(additional_row)

    # Prepare data for the third table (Salary Details)
    salary_table_data = [
        [Paragraph('<b></b>', styles['Normal']), Paragraph('<b>Standard</b>', styles['Normal']),
         Paragraph('<b>Actual</b>', styles['Normal']), Paragraph('<b></b>', styles['Normal']),
         Paragraph('<b>Standard</b>', styles['Normal']), Paragraph('<b>Actual</b>', styles['Normal'])],
        ['Basic Pay', salary_details.basic_salary, salary_details.basic_salary, 'PF', salary_details.pf, salary_details.pf],
        ['HRA', salary_details.hra, salary_details.hra, 'PT', '200', '200'],  # Replace with actual data
        ['Education Allowance', salary_details.education_allowance, salary_details.education_allowance, 'LWF', '', '100'],
        ['Statutory Bonus', salary_details.bonus, salary_details.bonus, 'ESIC', '', '150'],
        ['LTA', '', '', 'Income Tax', '', '500'],
        ['Conveyance', salary_details.conveyance_allowance, salary_details.conveyance_allowance, 'Loan', '', ''],
        ['', '', '', '', '', ''],
        [Paragraph('<b>Total Earnings</b>', styles['Normal']), salary_details.total, '', Paragraph('<b>Total Deduction</b>', styles['Normal']), '', '2000'],
        [Paragraph('<b>Net Salary</b>', styles['Normal']), salary_details.total - 2000, '', '', '', '']
    ]

    # Create a table for Salary Details and style
    table_salary = Table(salary_table_data, colWidths=[100, 100, 100, 100, 100, 100], repeatRows=1, hAlign='CENTER')
    table_salary.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ]))

    # Add Salary Details table to the story
    story.append(table_salary)

    # Add separate table with one column and one row
    one_cell_table_data = [[Paragraph('<b>In Words:</b> Eighteen Thousand Only', styles['Normal'])]]  # Update with actual amount in words
    table_one_cell = Table(one_cell_table_data, colWidths=[sum([100, 100, 100, 100, 100, 100])], hAlign='CENTER')
    table_one_cell.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    # Add the one-cell table to the story
    story.append(Spacer(1, 12))
    story.append(table_one_cell)
    story.append(Spacer(1, 12))

    # Add text below the table
    story.append(Paragraph('This is a computer-generated document. No signature is required.', styles['Normal']))

    # Build the PDF and save it to the buffer
    doc.build(story, onFirstPage=lambda canvas, doc: add_page_elements(canvas, doc, header_image_path, footer_image_path, watermark_image_path),
              onLaterPages=lambda canvas, doc: add_page_elements(canvas, doc, header_image_path, footer_image_path, watermark_image_path))

    # Get PDF data from buffer
    pdf_data = buffer.getvalue()
    buffer.close()

    # Create a response with PDF content
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="salary_slip.pdf"'

    return response









# @role_required('superuser')


# @role_required('fo')


# @role_required('company')

