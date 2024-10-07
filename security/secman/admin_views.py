from django.db import transaction, IntegrityError
from django.http import HttpResponse
from django.core.files.base import ContentFile
import io
from django.http import FileResponse
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.contrib.staticfiles import finders
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
from .models import EmployeeJoining, Attendance
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
from .models import Attendance, EmployeeJoining,AdvancePayment
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







@role_required('superuser')
def add_emp(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                print("Starting to process the form...")

                # Employee data extraction
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

                print(f"Emp ID: {emp_id}, First name: {first_name}, Last name: {last_name}")

                # Fetch the company
                company_id = request.POST.get('company')
                company = None
                if company_id:
                    try:
                        company = UserProfile.objects.get(id=company_id, user_type='company')
                        print(f"Selected company: {company}")
                    except UserProfile.DoesNotExist:
                        return render(request, 'admin/add_emp.html', {'error': 'Selected company does not exist or is not valid.'})

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
                print("Employee saved successfully.")

                # Salary details data extraction
                try:
                    salary_details = SalaryDetails(
                        employee=employee,  # Link to the employee instance
                        basic_salary=int(float(request.POST.get('basic_salary', 0))),
                        special_allowance=int(float(request.POST.get('special_allowance', 0))),
                        total=int(float(request.POST.get('total', 0))),
                        conveyance_allowance=int(float(request.POST.get('conveyance_allowance', 0))),
                        education_allowance=int(float(request.POST.get('education_allowance', 0))),
                        travelling_allowance=int(float(request.POST.get('travelling_allowance', 0))),
                        hours_daily_duty=int(float(request.POST.get('hours_daily_duty', 0))),
                        hra=int(float(request.POST.get('hra', 0))),
                        pf=int(float(request.POST.get('pf', 0))),
                        gratuity=int(float(request.POST.get('gratuity', 0))),
                        leave_with_wages=int(float(request.POST.get('leave_with_wages', 0))),
                        esic=int(float(request.POST.get('esic', 0))),
                        paid_holiday=int(float(request.POST.get('paid_holiday', 0))),
                        bonus=int(float(request.POST.get('bonus', 0))),
                        uniform=int(float(request.POST.get('uniform', 0))),
                        total_b=int(float(request.POST.get('total_b', 0))),
                        total_c=int(float(request.POST.get('total_c', 0))),
                        food_allowance=int(float(request.POST.get('food_allowance', 0))),
                        price_partial_uniform=int(float(request.POST.get('price_partial_uniform', 0))),
                        actual_salary=float(request.POST.get('actual_salary', 0.00)),
                        replicated_basic_salary=int(float(request.POST.get('basic_salary', 0))),
                        replicated_special_allowance=int(float(request.POST.get('special_allowance', 0))),
                        replicated_total=int(float(request.POST.get('total', 0))),
                        replicated_conveyance_allowance=int(float(request.POST.get('conveyance_allowance', 0))),
                        replicated_education_allowance=int(float(request.POST.get('education_allowance', 0))),
                        replicated_travelling_allowance=int(float(request.POST.get('travelling_allowance', 0))),
                        replicated_hours_daily_duty=int(float(request.POST.get('hours_daily_duty', 0))),
                        replicated_hra=int(float(request.POST.get('hra', 0))),
                        replicated_pf=int(float(request.POST.get('pf', 0))),
                        replicated_gratuity=int(float(request.POST.get('gratuity', 0))),
                        replicated_leave_with_wages=int(float(request.POST.get('leave_with_wages', 0))),
                        replicated_esic=int(float(request.POST.get('esic', 0))),
                        replicated_paid_holiday=int(float(request.POST.get('paid_holiday', 0))),
                        replicated_bonus=int(float(request.POST.get('bonus', 0))),
                        replicated_total_b=int(float(request.POST.get('total_b', 0))),
                        replicated_total_c=int(float(request.POST.get('total_c', 0))),
                        replicated_food_allowance=int(float(request.POST.get('food_allowance', 0))),
                        replicated_actual_salary=float(request.POST.get('actual_salary', 0.00)),
                    )
                    salary_details.save()
                    print("Salary details saved successfully.")
                except Exception as e:
                    print(f"Error saving salary details: {e}")
                    return render(request, 'admin/add_emp.html', {'error': 'Error saving salary details. Please check the data and try again.'})

                # Advance payment creation
                advance_amount = request.POST.get('advance_amount', None)
                if advance_amount:
                    advance_payment = AdvancePayment(
                        employee=employee,
                        salary_details=salary_details,
                        advance_amount=float(advance_amount),
                        request_status='Pending',
                        request_date=timezone.now(),
                    )
                    advance_payment.save()
                    print("Advance payment saved successfully.")

                # Generate and save the employee's PDF
                pdf_data = generate_employee_pdf(employee)
                employee.pdf_file.save(f'{employee.emp_id}_details.pdf', ContentFile(pdf_data))
                print("PDF generated and saved successfully.")

                # Provide the generated PDF for download
                response = HttpResponse(pdf_data, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{employee.emp_id}_details.pdf"'

                return response
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return render(request, 'admin/add_emp.html', {'error': 'Employee ID already exists. Please use a unique Employee ID.'})
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return render(request, 'admin/add_emp.html', {'error': 'An unexpected error occurred. Please try again.'})

    # If GET request, render the form with a list of companies
    companies = UserProfile.objects.filter(user_type='company')
    return render(request, 'admin/add_emp.html', {'companies': companies})


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


@role_required('superuser')
def admin_addshift(request):
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
    return render(request, 'admin/admin_addshift.html')

@role_required('superuser')
def admin_shift_list(request):
    shifts = ShiftTime.objects.all()  # Fetch all ShiftTime records
    return render(request, 'admin/admin_shift_list.html', {'shifts': shifts})


@role_required('superuser')
def admin_markattendance(request):
    if request.method == 'GET':
        company_id = request.GET.get('company', None)
        date = request.GET.get('date', timezone.now().date())

        companies = UserProfile.objects.filter(user_type='company')

        if company_id:
            try:
                company = UserProfile.objects.get(id=company_id, user_type='company')
                employees = EmployeeJoining.objects.filter(company=company)
            except UserProfile.DoesNotExist:
                messages.error(request, "Company not found")
                employees = []
            shifts = ShiftTime.objects.all()
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

        return render(request, 'admin/admin_markattendance.html', context)
    

    


from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from .models import Attendance, ShiftTime

def admin_submit_attendance(request):
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

        return redirect('admin_markattendance')
    else:
        return HttpResponseBadRequest("Invalid request method")    


#################################################################################################################################################################################
@role_required('superuser')
def admin_company_list(request):
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
    
    return render(request, 'admin/admin_company_list.html', {'company_data': company_data})

@role_required('superuser')
def admin_company_employees(request, company_id):
    company = get_object_or_404(UserProfile, id=company_id, user_type='company')
    guards = EmployeeJoining.objects.filter(company=company, position='Security Guard')
    supervisors = EmployeeJoining.objects.filter(company=company, position='Supervisor')
    return render(request, 'admin/admin_company_employees.html', {
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
@role_required('superuser')
def admin_create_tax_invoice(request):
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

    return redirect('admin/admin_company_list')



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
        [company_to_send, f"PO Number: {po}", ""],  # Example data
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
    "       •   Account Number: 776601010050222          IFSC Code: UBIN0577669 . \n"
    "       •   Bank Name: Union Bank of India              Branch Name: Wagoli, Pune .\n"
    "       •   Interest @24% P.A. will be charged if the bill is not paid before the due date as per contract.\n"
    "       •   Kindly pay by cheque/demand draft in favour of Best Security Services.\n"
    "       •   For prompt updation of payment, an advice with details is a must.\n"
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



from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, DecimalField, F
from django.db.models.functions import Cast
from datetime import datetime
from decimal import Decimal

from .models import SalaryDetails, Attendance, AdvancePayment
@role_required('superuser')
def admin_salarysheet(request):
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # Get the number of days in the current month
    days_in_month = (datetime(current_year, current_month + 1, 1) - datetime(current_year, current_month, 1)).days

    # Get all salary details
    salary_details_list = SalaryDetails.objects.all()

    # Process form submission
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('basic_salary_'):
                salary_id = key.split('_')[-1]
                salary = get_object_or_404(SalaryDetails, id=salary_id)
                try:
                    # Update fields
                    salary.basic_salary = Decimal(request.POST.get(f'basic_salary_{salary_id}', salary.basic_salary))
                    salary.special_allowance = Decimal(request.POST.get(f'special_allowance_{salary_id}', salary.special_allowance))
                    salary.total = Decimal(request.POST.get(f'total_{salary_id}', salary.total))
                    salary.conveyance_allowance = Decimal(request.POST.get(f'conveyance_allowance_{salary_id}', salary.conveyance_allowance))
                    salary.education_allowance = Decimal(request.POST.get(f'education_allowance_{salary_id}', salary.education_allowance))
                    salary.travelling_allowance = Decimal(request.POST.get(f'travelling_allowance_{salary_id}', salary.travelling_allowance))
                    salary.hours_daily_duty = Decimal(request.POST.get(f'hours_daily_duty_{salary_id}', salary.hours_daily_duty))
                    salary.total_b = Decimal(request.POST.get(f'total_b_{salary_id}', salary.total_b))
                    salary.hra = Decimal(request.POST.get(f'hra_{salary_id}', salary.hra))
                    salary.pf = Decimal(request.POST.get(f'pf_{salary_id}', salary.pf))
                    salary.gratuity = Decimal(request.POST.get(f'gratuity_{salary_id}', salary.gratuity))
                    salary.leave_with_wages = Decimal(request.POST.get(f'leave_with_wages_{salary_id}', salary.leave_with_wages))
                    salary.esic = Decimal(request.POST.get(f'esic_{salary_id}', salary.esic))
                    salary.paid_holiday = Decimal(request.POST.get(f'paid_holiday_{salary_id}', salary.paid_holiday))
                    salary.bonus = Decimal(request.POST.get(f'bonus_{salary_id}', salary.bonus))
                    salary.uniform = Decimal(request.POST.get(f'uniform_{salary_id}', salary.uniform))
                    salary.total_c = Decimal(request.POST.get(f'total_c_{salary_id}', salary.total_c))
                    salary.food_allowance = Decimal(request.POST.get(f'food_allowance_{salary_id}', salary.food_allowance))
                    salary.price_partial_uniform = Decimal(request.POST.get(f'price_partial_uniform_{salary_id}', salary.price_partial_uniform))
                    salary.actual_salary = Decimal(request.POST.get(f'actual_salary_{salary_id}', salary.actual_salary))
                    
                    salary.save()
                except Exception as e:
                    print(f"Error updating salary {salary_id}: {e}")
        
        return redirect('admin_salarysheet')

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
        total_c = Decimal(salary.total_c)
        actual_daily_wages = Decimal(total_c / days_in_month)

        # Get approved advance payments for the employee
        approved_advance = AdvancePayment.objects.filter(
            employee=salary.employee,
            request_status='Approved',
            request_date__month=current_month,
            request_date__year=current_year
        ).aggregate(total_advance=Sum('advance_amount'))['total_advance'] or Decimal('0')

        # Calculate the actual salary
        actual_salary = actual_daily_wages * days_present - approved_advance - Decimal(salary.food_allowance) - Decimal(salary.price_partial_uniform)

        salary_with_actual.append({
            'salary': salary,
            'actual_salary': actual_salary,
            'approved_advance': approved_advance
        })

    return render(request, 'admin/admin_salarysheet.html', {'salary_with_actual': salary_with_actual})




@role_required('superuser')
def update_salary(request, salary_id):
    salary = get_object_or_404(SalaryDetails, pk=salary_id)

    if request.method == 'POST':
        # Update fields
        salary.basic_salary = request.POST.get('basic_salary')
        salary.special_allowance = request.POST.get('special_allowance')
        salary.total = request.POST.get('total')
        salary.conveyance_allowance = request.POST.get('conveyance_allowance')
        salary.education_allowance = request.POST.get('education_allowance')
        salary.travelling_allowance = request.POST.get('travelling_allowance')
        salary.hours_daily_duty = request.POST.get('hours_daily_duty')
        salary.total_b = request.POST.get('total_b')
        salary.hra = request.POST.get('hra')
        salary.pf = request.POST.get('pf')
        salary.gratuity = request.POST.get('gratuity')
        salary.leave_with_wages = request.POST.get('leave_with_wages')
        salary.esic = request.POST.get('esic')
        salary.paid_holiday = request.POST.get('paid_holiday')
        salary.bonus = request.POST.get('bonus')
        salary.uniform = request.POST.get('uniform')
        salary.advance_payment = request.POST.get('advance_payment')
        salary.price_partial_uniform = request.POST.get('price_partial_uniform')
        salary.food_allowance = request.POST.get('food_allowance')
        salary.total_c = request.POST.get('total_c')
        salary.actual_salary = request.POST.get('actual_salary')
        
        salary.save()
        return redirect('admin_salarysheet')

    return render(request, 'admin/update_salary.html', {'salary': salary})

# views.py





@role_required('superuser')
def admin_present(request):
    companies = UserProfile.objects.filter(user_type='company')
    return render(request, 'admin/admin_present.html', {'companies': companies})

def admin_get_employees(request):
    company_id = request.GET.get('company_id')
    employees = EmployeeJoining.objects.filter(company_id=company_id).values('emp_id', 'first_name', 'last_name')
    employees_list = list(employees)
    return JsonResponse(employees_list, safe=False)



# views.py


@role_required('superuser')
def admin_monthly_attendance(request, emp_id):
    employee = get_object_or_404(EmployeeJoining, emp_id=emp_id)
    
    # Get the current year and month or use provided query parameters
    now = datetime.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    # Filter attendance records by the selected month and year
    attendance_records = Attendance.objects.filter(employee_id=employee.id, date__year=year, date__month=month)

    # Create a list of months for the dropdown
    months = [(i, datetime.strptime(str(i), '%m').strftime('%B')) for i in range(1, 13)]

    return render(request, 'admin/admin_monthlyattendance.html', {
        'employee': employee,
        'attendance_records': attendance_records,
        'year': year,
        'month': month,
        'months': months,
    })
    
    
from django.contrib import messages


@role_required('superuser')
def admin_advance_options(request, emp_id):
    employee = get_object_or_404(EmployeeJoining, emp_id=emp_id)
    salary_details = get_object_or_404(SalaryDetails, employee=employee)

    if request.method == 'POST':
        advance_amount = request.POST.get('advance_amount', 0)
        try:
            advance_amount = float(advance_amount)
        except ValueError:
            messages.error(request, "Invalid advance amount.")
            return render(request, 'admin/admin_advance.html', {'employee': employee, 'salary_details': salary_details})

        if advance_amount > salary_details.basic_salary:
            messages.error(request, "Advance amount cannot be greater than the basic salary.")
            return render(request, 'admin/admin_advance.html', {'employee': employee, 'salary_details': salary_details})

        # Save the advance amount to the SalaryDetails model
        salary_details.advance_payment = advance_amount
        salary_details.save()

        messages.success(request, "Advance amount recorded successfully.")
        return redirect('dashboard', emp_id=emp_id)

    return render(request, 'admin/admin_advance.html', {'employee': employee, 'salary_details': salary_details})

@role_required('superuser')
def admin_mess_view(request, emp_id):
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
    return render(request, 'admin/admin_mess.html', context)

@role_required('superuser')
def admin_partial_uniform_view(request, emp_id):
    salary_detail = get_object_or_404(SalaryDetails, employee__emp_id=emp_id)
    employees = EmployeeJoining.objects.get(emp_id=emp_id)
    
    if request.method == 'POST':
        uniform_status = request.POST.get('partialuniform')
        employees.partialuniform = uniform_status
        new_price_partial_uniform = request.POST.get('price_partial_uniform')
        salary_detail.price_partial_uniform = new_price_partial_uniform
        salary_detail.save()
        employees.save()
        return redirect(reverse('admin_partial_uniform', args=[emp_id]))

    context = {
        'salary_detail': salary_detail,
        'employees':employees,
        'employee': salary_detail.employee,
    }
    return render(request, 'admin/admin_partial_uniform.html', context)


@role_required('superuser')
def admin_advance(request, employee_id):
    employee = get_object_or_404(EmployeeJoining, emp_id=employee_id)
    salary_details = get_object_or_404(SalaryDetails, employee=employee)

    if request.method == 'POST':
        if salary_details.advance_request_status == 'Pending':
            advance_amount = request.POST.get('advance_amount')
            
            # Store the requested advance in SalaryDetails
            salary_details.advance_payment = advance_amount
            salary_details.advance_request_status = 'Pending'
            salary_details.advance_payment_approval_date = timezone.now()
            salary_details.save()

            # Send a notification to the admin (this can be done via email, dashboard notification, etc.)
            messages.success(request, 'Advance request submitted successfully. Waiting for admin approval.')

        else:
            messages.error(request, 'Advance payment request has already been processed.')

        return redirect('admin_present')

    return render(request, 'admin/admin_advance.html', {'employee': employee, 'salary_details': salary_details})



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.core.files.base import ContentFile
from .models import EmployeeJoining, SalaryDetails, UserProfile

@role_required('superuser')
def admin_update_emp(request, emp_id):
    employee = get_object_or_404(EmployeeJoining, emp_id=emp_id)
    salary_details = get_object_or_404(SalaryDetails, employee=employee)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update Employee data
                employee.first_name = request.POST['first_name']
                employee.middle_name = request.POST.get('middle_name', '')
                employee.last_name = request.POST['last_name']
                employee.contact_number = request.POST['contact_number']
                employee.age = request.POST['age']
                employee.gender = request.POST['gender']
                employee.current_address = request.POST['current_address']
                employee.permanent_address = request.POST['permanent_address']
                employee.city = request.POST['city']
                employee.state = request.POST['state']
                employee.pincode = request.POST['pincode']
                employee.date_of_birth = request.POST['date_of_birth']
                employee.emergency_contact1 = request.POST['emergency_contact1']
                employee.emergency_contact_relation1 = request.POST['emergency_contact_relation1']
                employee.emergency_contact_relation1_name = request.POST['emergency_contact_relation1_name']
                employee.pancard = request.POST['pancard']
                employee.aadhar = request.POST['aadhar']
                employee.voter = request.POST['voter']
                employee.security_guard_training = request.POST.get('security_guard_training') == 'yes'
                employee.job_experience = request.POST.get('job_experience') == 'yes'
                
                # Update profile picture and signature if new files are uploaded
                if 'profile_picture' in request.FILES:
                    employee.profile_picture = request.FILES['profile_picture']
                if 'signature' in request.FILES:
                    employee.signature = request.FILES['signature']

                employee.preferred_work_arrangements = request.POST['preferred_work_arrangements']
                employee.position = request.POST['position']
                employee.account_holder_name = request.POST['account_holder_name']
                employee.bank_name = request.POST['bank_name']
                employee.bank_account_number = request.POST['bank_account_number']
                employee.ifsc_code = request.POST['ifsc_code']
                employee.branch_name = request.POST['branch_name']
                employee.bank_address = request.POST['bank_address']
                employee.qualification = request.POST['qualification']
                employee.experience = request.POST['experience']

                # Update company data
                company_id = request.POST.get('company')
                if company_id:
                    try:
                        company = UserProfile.objects.get(id=company_id, user_type='company')
                        employee.company = company
                    except UserProfile.DoesNotExist:
                        return render(request, 'admin/update_emp.html', {'employee': employee, 'error': 'Selected company does not exist or is not valid.'})

                employee.save()

                # Update Salary details data
                salary_details.basic_salary = int(float(request.POST['basic_salary']))
                salary_details.special_allowance = int(float(request.POST['special_allowance']))
                salary_details.total = int(float(request.POST['total']))
                salary_details.conveyance_allowance = int(float(request.POST['conveyance_allowance']))
                salary_details.education_allowance = int(float(request.POST['education_allowance']))
                salary_details.travelling_allowance = int(float(request.POST['travelling_allowance']))
                salary_details.hours_daily_duty = int(float(request.POST['hours_daily_duty']))
                salary_details.hra = int(float(request.POST['hra']))
                salary_details.pf = int(float(request.POST['pf']))
                salary_details.gratuity = int(float(request.POST['gratuity']))
                salary_details.leave_with_wages = int(float(request.POST['leave_with_wages']))
                salary_details.esic = int(float(request.POST['esic']))
                salary_details.paid_holiday = int(float(request.POST['paid_holiday']))
                salary_details.bonus = int(float(request.POST['bonus']))
                salary_details.uniform = int(float(request.POST['uniform']))
                salary_details.total_b = int(float(request.POST['total_b']))
                salary_details.total_c = int(float(request.POST['total_c']))
                # salary_details.advance_payment = int(float(request.POST.get('advance_payment', 0)))
                salary_details.food_allowance = request.POST.get('food_allowance', 0)

                salary_details.save()

                # Generate PDF
                pdf_data = generate_employee_pdf(employee)

                # Save PDF to the model instance
                employee.pdf_file.save(f'{employee.emp_id}_details.pdf', ContentFile(pdf_data))

                return redirect('admin_update_emp', emp_id=employee.emp_id)  # Redirect to some detail page or another view after saving

        except IntegrityError:
            return render(request, 'admin/update_emp.html', {'employee': employee, 'error': 'An error occurred while updating the employee details. Please try again.'})

    # If GET request, render the form with existing data
    companies = UserProfile.objects.filter(user_type='company')

    return render(request, 'admin/update_emp.html', {
        'employee': employee,
        'salary_details': salary_details,
        'companies': companies
    })


from io import BytesIO
from .models import Quotations
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render
from .models import Quotations

@role_required('superuser')
def security_quotation(request):
    if request.method == 'POST':
        # Extract data from POST request for Guard fields
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
        guard_total_c = request.POST.get('guard_total_c')
        guard_service_charges = request.POST.get('guard_service_charges')
        guard_grand_total_per_month = request.POST.get('guard_grand_total_per_month')

        # Extract data for Supervisor fields with default values of 0.0
        supervisor_basic_pay = request.POST.get('supervisor_basic_pay') or '0.0'
        supervisor_special_allowance = request.POST.get('supervisor_special_allowance') or '0.0'
        supervisor_total_a = request.POST.get('supervisor_total_a') or '0.0'
        supervisor_conveyance_allowance = request.POST.get('supervisor_conveyance_allowance') or '0.0'
        supervisor_education_allowance = request.POST.get('supervisor_education_allowance') or '0.0'
        supervisor_travelling_allowance = request.POST.get('supervisor_travelling_allowance') or '0.0'
        supervisor_house_duty = request.POST.get('supervisor_house_duty') or '0.0'
        supervisor_total_b = request.POST.get('supervisor_total_b') or '0.0'
        supervisor_washing_allowance = request.POST.get('supervisor_washing_allowance') or '0.0'
        supervisor_hra = request.POST.get('supervisor_hra') or '0.0'
        supervisor_sub_total_c = request.POST.get('supervisor_sub_total_c') or '0.0'
        supervisor_pf = request.POST.get('supervisor_pf') or '0.0'
        supervisor_gratuity = request.POST.get('supervisor_gratuity') or '0.0'
        supervisor_leave_with_wages = request.POST.get('supervisor_leave_with_wages') or '0.0'
        supervisor_esic = request.POST.get('supervisor_esic') or '0.0'
        supervisor_paid_holiday = request.POST.get('supervisor_paid_holiday') or '0.0'
        supervisor_bonus = request.POST.get('supervisor_bonus') or '0.0'
        supervisor_uniform = request.POST.get('supervisor_uniform') or '0.0'
        supervisor_total_c = request.POST.get('supervisor_total_c') or '0.0'
        supervisor_service_charges = request.POST.get('supervisor_service_charges') or '0.0'
        supervisor_grand_total_per_month = request.POST.get('supervisor_grand_total_per_month') or '0.0'

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
            supervisor_total_c=supervisor_total_c,
            supervisor_service_charges=supervisor_service_charges,
            supervisor_grand_total_per_month=supervisor_grand_total_per_month
        )
        quotation.save()
        
        # Generate PDF
        pdf = generate_quotation_pdf_security(quotation)
        pdf_file = ContentFile(pdf, 'quotation.pdf')
        quotation.pdf_file.save('quotation.pdf', pdf_file)
        quotation.save()

        # Return the PDF as a downloadable response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="quotation.pdf"'
        return response

    return render(request, 'admin/security_quotation.html')




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
        ['SR. No. 1', 'Particulars', 'Security Guard 30/31 Days (12 Hours )'], 
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





@role_required('superuser')
def emp_list(request):
    # Get the selected company from the request parameters (if provided)
    company_id = request.GET.get('company_id')
    
    if company_id:
        # Filter employees based on the selected company (using the company field directly)
        employees = EmployeeJoining.objects.filter(company_id=company_id)
    else:
        # If no company is selected, list all employees
        employees = EmployeeJoining.objects.all()
    
    # Fetch all companies for the dropdown filter
    companies = UserProfile.objects.filter(user_type='company')
    
    return render(request, 'admin/emp_list.html', {
        'employees': employees,
        'companies': companies,  # Pass companies to the template for the filter dropdown
        'selected_company': company_id  # To know which company is selected
    })






def view_pdf(request, emp_id):
    employee = get_object_or_404(EmployeeJoining, id=emp_id)
    
    if employee.pdf_file:
        response = FileResponse(open(employee.pdf_file.path, 'rb'))
        return response
    else:
        return HttpResponse("No PDF found for this employee.")






