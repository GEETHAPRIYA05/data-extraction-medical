from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string, get_template
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Patient, Appointment, Staff, Prescription, CaseStudy, DoctorSchedule
from django.shortcuts import render, redirect
from .forms import CaseStudyForm
from django.contrib import messages
import pdfkit
import io

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def send_chat_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        user_email = request.user.email if request.user.is_authenticated else 'Anonymous User'

        send_mail(
            subject="New Chat Message from LifeSpring Portal",
            message=f"From: {user_email}\n\nMessage:\n{message}",
            from_email='atgeethapriya2004@gmail.com',       # same as EMAIL_HOST_USER
    recipient_list=['atgeethapriya2004@gmail.com'],  # you receive it here
            fail_silently=False,
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def splash_view(request):
    return render(request, 'splash.html')

def login_view(request):
    return render(request, 'login.html')

# ---- LOGIN ----
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


# ---- PATIENT VIEWS ----
def patient_dashboard(request):
    search_query = request.GET.get('search', '').strip()
    if search_query:
        patients = Patient.objects.filter(name__icontains=search_query)
    else:
        patients = Patient.objects.all()
    return render(request, 'patient_dashboard.html', {
        'patients': patients,
        'search_query': search_query
    })


def add_patient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact', '')
        medical_history = request.POST.get('medical_history', '')
        allergies = request.POST.get('allergies', '')
        medications = request.POST.get('medications', '')

        if not (name and age and gender):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'add_patient.html')

        patient, created = Patient.objects.get_or_create(
            name=name,
            defaults={
                'age': age,
                'gender': gender,
                'contact': contact,
                'medical_history': medical_history,
                'allergies': allergies,
                'medications': medications
            }
        )

        if created:
            messages.success(request, f'Patient "{name}" added successfully!')
        else:
            messages.warning(request, f'Patient "{name}" already exists.')

        return redirect('patient_dashboard')

    return render(request, 'add_patient.html')


def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.age = request.POST.get('age')
        patient.gender = request.POST.get('gender')
        patient.contact = request.POST.get('contact')
        patient.medical_history = request.POST.get('medical_history')
        patient.allergies = request.POST.get('allergies')
        patient.medications = request.POST.get('medications')
        patient.save()
        messages.success(request, f"Patient '{patient.name}' updated successfully!")
        return redirect('patient_dashboard')
    return render(request, 'edit_patient.html', {'patient': patient})


def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    patient.delete()
    messages.success(request, f"Patient '{patient.name}' deleted successfully!")
    return redirect('patient_dashboard')


# ---- APPOINTMENT VIEWS ----
def appointments(request):
    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        appointments_list = Appointment.objects.filter(
            patient__name__icontains=search_query
        ).order_by('-date', '-time')
    else:
        appointments_list = Appointment.objects.all().order_by('-date', '-time')

    return render(request, 'appointments.html', {
        'appointments': appointments_list,
        'search_query': search_query
    })


def add_appointment(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient')
        date = request.POST.get('date')
        time = request.POST.get('time')
        doctor = request.POST.get('doctor')
        reason = request.POST.get('reason')
        status = request.POST.get('status')

        # ✅ Automatically create patient if not found
        patient, created = Patient.objects.get_or_create(name=patient_name)

        Appointment.objects.create(
            patient=patient,
            date=date,
            time=time,
            doctor=doctor,
            reason=reason,
            status=status
        )
        messages.success(request, "Appointment added successfully!")
        return redirect('add_appointment')

    return render(request, 'add_appointment.html')


def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    if request.method == 'POST':
        patient_name = request.POST.get('patient')
        patient, _ = Patient.objects.get_or_create(name=patient_name)
        appointment.patient = patient
        appointment.date = request.POST.get('date')
        appointment.time = request.POST.get('time')
        appointment.doctor = request.POST.get('doctor')
        appointment.reason = request.POST.get('reason')
        appointment.status = request.POST.get('status')
        appointment.save()
        messages.success(request, "Appointment updated successfully!")
        return redirect('appointments')

    return render(request, 'edit_appointment.html', {'appointment': appointment})


def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    appointment.delete()
    messages.success(request, "Appointment deleted successfully!")
    return redirect('appointments')


# ---- STAFF VIEWS ----
def staff_management(request):
    search_query = request.GET.get('search', '').strip()
    if request.method == "POST":
        name = request.POST.get("name")
        role = request.POST.get("role")
        department = request.POST.get("department")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        address = request.POST.get("address")
        Staff.objects.create(
            name=name, role=role, department=department,
            contact=contact, email=email, address=address
        )
        messages.success(request, "Staff added successfully!")
        return redirect("staff_management")

    if search_query:
        staff = Staff.objects.filter(name__icontains=search_query)
    else:
        staff = Staff.objects.all()

    return render(request, "staff_management.html", {
        "staff": staff,
        "search_query": search_query
    })


def edit_staff(request, id):
    staff = get_object_or_404(Staff, id=id)
    if request.method == "POST":
        staff.name = request.POST.get("name")
        staff.role = request.POST.get("role")
        staff.department = request.POST.get("department")
        staff.contact = request.POST.get("contact")
        staff.email = request.POST.get("email")
        staff.address = request.POST.get("address")
        staff.save()
        messages.success(request, "Staff updated successfully!")
        return redirect("staff_management")
    return render(request, "edit_staff.html", {"staff_member": staff})


def delete_staff(request, id):
    staff = get_object_or_404(Staff, id=id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect("staff_management")


# ---- DASHBOARD ----
@never_cache
def dashboard(request):

    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    total_doctors = 4
    total_departments = 8

    patients = Patient.objects.all().order_by('-id')[:5]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_departments': total_departments,
        'total_appointments': total_appointments,
        'patients': patients,
    }
    return render(request, 'dashboard.html', context)


# ---- AJAX ENDPOINTS FOR AUTO-UPDATE ----
@never_cache
def get_dashboard_counts(request):
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    total_doctors = 2
    total_departments = 4
    return JsonResponse({
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_doctors': total_doctors,
        'total_departments': total_departments,
    })


@never_cache
def get_recent_patients(request):
    patients = Patient.objects.all().order_by('-id')[:5]
    data = [
        {
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "contact": p.contact,
        }
        for p in patients
    ]
    return JsonResponse({"patients": data})

def case_studies(request):
    return render(request, 'case_studies.html')

def doctor_schedule(request):
    return render(request, 'doctor_schedule.html')

def report(request):
    return render(request, 'report.html')

def prescription_form(request):
    if request.method == 'POST':
        doctor_name = request.POST.get('doctor_name')
        date = request.POST.get('date')
        patient_name = request.POST.get('patient_name')
        age = request.POST.get('age')
        diagnosis = request.POST.get('diagnosis')

        # Handle multiple medicine rows
        medicine_names = request.POST.getlist('medicine_name[]')
        dosages = request.POST.getlist('dosage[]')
        frequencies = request.POST.getlist('frequency[]')
        durations = request.POST.getlist('duration[]')
        remarks_list = request.POST.getlist('remarks[]')

        for i in range(len(medicine_names)):
            Prescription.objects.create(
                doctor_name=doctor_name,
                date=date,
                patient_name=patient_name,
                age=age,
                diagnosis=diagnosis,
                medicine_name=medicine_names[i],
                dosage=dosages[i],
                frequency=frequencies[i],
                duration=durations[i],
                remarks=remarks_list[i],
            )

        messages.success(request, "Prescription saved successfully!")
        return render(request, 'prescriptions.html', {'success': True})

    return render(request, 'prescriptions.html')

def view_prescriptions(request):
    query = request.GET.get('search')
    if query:
        prescriptions = Prescription.objects.filter(patient_name__icontains=query)
    else:
        prescriptions = Prescription.objects.all().order_by('-date')
    return render(request, 'view_prescriptions.html', {'prescriptions': prescriptions, 'query': query})


def prescription_pdf(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    html = render_to_string('prescription_pdf.html', {'prescription': prescription})
    pdf = pdfkit.from_string(html, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"Prescription_{prescription.patient_name}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'  # use inline for browser view
    return response

def prescription_pdf(request, pk):
    # Fetch the specific prescription
    prescription = get_object_or_404(Prescription, pk=pk)

    # Load the HTML template for PDF rendering
    template = get_template('prescription_pdf.html')
    html = template.render({'prescription': prescription})

    # ✅ Path to wkhtmltopdf.exe (make sure this exists)
    pdf_path = r"d:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

    # Configure pdfkit to use wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf=pdf_path)

    # Generate PDF from HTML string
    pdf = pdfkit.from_string(html, False, configuration=config)

    # Return as downloadable file
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_{pk}.pdf"'
    return response

def case_studies(request):
    case_studies = CaseStudy.objects.all()
    return render(request, 'case_studies.html', {'case_studies': case_studies})

def add_case_study(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        diagnosis = request.POST.get('diagnosis')
        treatment = request.POST.get('treatment')
        outcome = request.POST.get('outcome')

        CaseStudy.objects.create(
            patient_name=patient_name,
            diagnosis=diagnosis,
            treatment=treatment,
            outcome=outcome
        )
        return redirect('case_studies')

    return render(request, 'add_case_study.html')

def edit_case_study(request, pk):
    case = get_object_or_404(CaseStudy, pk=pk)

    if request.method == 'POST':
        case.patient_name = request.POST.get('patient_name')
        case.diagnosis = request.POST.get('diagnosis')
        case.treatment = request.POST.get('treatment')
        case.outcome = request.POST.get('outcome')
        case.save()
        return redirect('case_studies')

    return render(request, 'edit_case_study.html', {'case': case})


def delete_case_study(request, pk):
    case = get_object_or_404(CaseStudy, pk=pk)
    case.delete()
    return redirect('case_studies')

def doctor_schedule(request):
    schedules = DoctorSchedule.objects.all()
    return render(request, 'doctor_schedule.html', {'schedules': schedules})

def add_doctor_schedule(request):
    if request.method == "POST":
        doctor_name = request.POST.get("doctor_name")
        weekday = request.POST.get("weekday")
        visiting_time = request.POST.get("visiting_time")
        status = request.POST.get("status")

        DoctorSchedule.objects.create(
            doctor_name=doctor_name,
            weekday=weekday,
            visiting_time=visiting_time,
            status=status
        )
        messages.success(request, "Doctor schedule added successfully!")
        return redirect('doctor_schedule')

    return render(request, "add_doctor_schedule.html")

def edit_doctor_schedule(request, id):
    schedule = get_object_or_404(DoctorSchedule, id=id)

    if request.method == "POST":
        schedule.doctor_name = request.POST.get("doctor_name")
        schedule.weekday = request.POST.get("weekday")
        schedule.visiting_time = request.POST.get("visiting_time")
        schedule.status = request.POST.get("status")
        schedule.save()
        messages.success(request, "Doctor schedule updated successfully!")
        return redirect("doctor_schedule")

    return render(request, "edit_doctor_schedule.html", {"schedule": schedule})

def delete_doctor_schedule(request, id):
    schedule = get_object_or_404(DoctorSchedule, id=id)
    schedule.delete()
    messages.success(request, "Doctor schedule deleted successfully!")
    return redirect("doctor_schedule")

def report_view(request):
    # Get all patients (we’ll display them in 3 summary tables in HTML)
    patients = Patient.objects.all()

    context = {
        'patients': patients,
    }
    return render(request, 'report.html', context)

def logout_view(request):
    logout(request)
    return render(request, 'logout.html')

def index_view(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"Message from: {name} <{email}>\n\n{message}"

        # send email (change to your email)
        send_mail(
            subject,
            full_message,
            email,  # from
           ['atgeethapriya2004@gmail.com'], # to
            fail_silently=False,
        )
   
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')

    return render(request, 'contact.html')

def delete_prescription(request, id):
    prescription = get_object_or_404(Prescription, id=id)
    prescription.delete()
    return redirect('view_prescriptions')
