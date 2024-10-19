import datetime
import http
import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import redirect

from api.models import ClearenceCode
from .forms import BootstrapAuthenticationForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from datetime import timedelta
from .models import *
from django.db.models import Count


@login_required
def home(request):
    users = CustomUser.objects.all()
    return render(request, 'user/users.html',context={"users":users})

@login_required
def getLink(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    parent = Parent.objects.all()
    attendance = Attendance.objects.filter(date=datetime.today())
    students = Student.objects.all()
    parent = len(parent)
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    if start_date and end_date:
        attendance = Attendance.objects.filter(date__range=[start_date, end_date])
    elif start_date:
        attendance = Attendance.objects.filter(date__gte=start_date)
    elif end_date:
        attendance = Attendance.objects.filter(date__lte=end_date)
    else:
        attendance = Attendance.objects.all()
    
    return render(request, 'user/Homes.html', {'users': attendance,"length":len(attendance),"parents":parent,"attendance":len(attendance),"students":len(students)})


@login_required
def Attendances(request):
    attendance_records = Attendance.objects.all()
    creator_name = request.GET.get('creator_name', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    if creator_name:
        attendance_records = attendance_records.filter(parent__parentname__icontains=creator_name)
    if start_date and end_date:
        attendance_records = attendance_records.filter(date__range=[start_date, end_date])
    
    print(attendance_records)
    context = {
        'attendance_records': attendance_records,
    }
    return render(request, 'user/Attendance.html',context)


def login_view(request):
    if request.method == 'POST':
        form = BootstrapAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = BootstrapAuthenticationForm()
    
    return render(request, 'user/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def delete_user(request, user_id):
    # Retrieve the user object or return 404 if not found
    user = get_object_or_404(CustomUser, pk=user_id)
    user.delete()
    users = CustomUser.objects.all()
    return redirect('users')


def make_user_superuser(request, user_id):
    try:
        user = get_object_or_404(CustomUser, pk=user_id)
        user.is_superuser = True
        user.save()
        return redirect('users')
    except user.DoesNotExist:
           return redirect('users')
    
def revoke_user_superuser(request, user_id):
    try:
        user = get_object_or_404(CustomUser, pk=user_id)
        user.is_superuser = False
        user.save()
        return redirect('users')
    except user.DoesNotExist:
           return redirect('users')
def get_logs(request):
    logs = Logs.objects.all()
    return render(request, 'user/logs.html', {'logs': logs})

def get_user_logs(request, user_id):
        user = get_object_or_404(CustomUser, pk=user_id)
        logs = Logs.objects.filter(user=user)
        return render(request, 'user/logsid.html', {'logs': logs,"user":user})


def Attendanc(request):
    return render(request, 'user/attendance.html')


def Teachers(request):
    users = Teacher.objects.all()
    allusers = []
    for user in users:
        isActive = Attendance.objects.filter(user=user, date=datetime.today())
        if isActive:
            user.isActive = True
        else:
            user.isActive = False
        allusers.append(user)

    return render(request, 'user/teachers.html',{'users':allusers})    

def Students(request):
    users = Student.objects.all()
    return render(request, 'user/students.html',{'users':users})

def Parents(request):
    users = Parent.objects.all()
    return render(request, 'user/parents.html',{'users':users})


def user_report(request, user_id):

    user = Student.objects.filter(user_id=user_id).first()
    
    # Handle date filtering
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        # Filter attendance for this user
        attendance = Attendance.objects.filter(user=user, date__range=[start_date, end_date])
        
        # Calculate total days excluding weekends
        total_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                total_days += 1
            current_date += timedelta(days=1)

        # Count attendance per day
        attendance_per_day = attendance.values('date').annotate(count=Count('id'))
        attendance_dict = {entry['date']: entry['count'] for entry in attendance_per_day}

        # Calculate missed days
        missed_days = total_days - sum(attendance_dict.values())

        chart_data = {
            "labels": ["Attended", "Missed"],
            "data": [sum(attendance_dict.values()), missed_days]
        }
        
        return render(request, 'user/report.html', {
            'attendance': attendance,
            'chart_data': chart_data,
            'start_date': start_date,
            'end_date': end_date,
            'user': user
        })
    else:
        # If no filters applied, show the full table
        attendance = Attendance.objects.filter(user=user)
        
        return render(request, 'user/report.html', {
            'attendance': attendance,
            'chart_data': None,  # No chart data when no filter is applied
            'start_date': None,
            'end_date': None,
            'user': user
        })

def delete_student(request, user_id):
    person = get_object_or_404(Student, user_id=user_id)
    
    if request.method == 'POST':
        person.delete()
        return redirect('person_list')  # Redirect to a list view or any other page
    
    return render(request, 'delete_person.html', {'person': person})

def delete_teacher(request, user_id):
    person = get_object_or_404(Teacher, user_id=user_id)
    
    if request.method == 'POST':
        person.delete()
        return redirect('person_list')  # Redirect to a list view or any other page
    
    return render(request, 'delete_person.html', {'person': person})

def delete_parent(request, user_id):
    person = get_object_or_404(Parent, user_id=user_id)
    
    if request.method == 'POST':
        person.delete()
        return redirect('person_list')  # Redirect to a list view or any other page
    
    return render(request, 'delete_person.html', {'person': person})





def edit_teacher(request, id):
    teacher = get_object_or_404(Person, user_id=id)

    if request.method == 'POST':
        # Get the data from request.POST for non-file fields and request.FILES for file fields
        name = request.POST.get('name')
        profile = request.FILES.get('profile')
        person_type = request.POST.get('person_type')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        officialphone = request.POST.get('officialphone')
        officialphonext = request.POST.get('officialphonext')
        is_official = request.POST.get('isOfficial') == 'true'
        saved = request.POST.get('saved') == 'true'

        # Update the teacher's fields manually
        teacher.name = name if name else teacher.name
        teacher.phone = phone if phone else teacher.phone
        teacher.email = email if email else teacher.email
        teacher.officialphone = officialphone if officialphone else teacher.officialphone
        teacher.officialphonext = officialphonext if officialphonext else teacher.officialphonext
        teacher.person_type = person_type if person_type else teacher.person_type
        teacher.isOfficial = is_official
        teacher.saved = saved

        # Handle the profile image if it's being updated
        if profile:
            teacher.profile = profile

        # Save the updated teacher object
        try:
            teacher.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        # Return teacher data if it's a GET request (if needed)
        teacher_data = {
            'name': teacher.name,
            'phone': teacher.phone,
            'email': teacher.email,
            'officialphone': teacher.officialphone,
            'officialphonext': teacher.officialphonext,
            'person_type': teacher.person_type,
            
            'profile_url': teacher.profile.url if teacher.profile else None,
        }
        return render(request, 'user/Editeacher.html', {'teacher_data': json.dumps(teacher_data)})


def getClearenceCodes(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    creator_name = request.GET.get('creator_name', '')


    filters = {}
    if start_date:
        filters['date_created__gte'] = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        filters['date_created__lte'] = datetime.strptime(end_date, '%Y-%m-%d')
    if creator_name:
        filters['created_by__parentname__icontains'] = creator_name

    codes = ClearenceCode.objects.filter(**filters)

    return render(request, 'user/Clearence.html', {"codes": codes})
    
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages

def add_clearance_code(request):
    if request.method == "POST":
        visitor_name = request.POST.get('visitor_name')
        visitor_contact = request.POST.get('visitor_contact')
        visitor_relationship = request.POST.get('visitor_relationship')
        reason = request.POST.get('reason')
        expiry_date = request.POST.get('expiry_date')
        is_active = request.POST.get('is_active') == 'on'
        clearence = ClearenceCode.objects.filter(visitor_contact=visitor_contact, expiry_date=expiry_date)
        if clearence:
            messages.error(request, 'Clearance Code already exists!')
            return render(request, 'user/Newcode.html')
    
        otp_value = random.randint(10000000, 99999999)
        otp_value_str = str(otp_value)
        parent = Parent.objects.get(parentname="Administrator")
        try:
            # Save the clearance code
            clearance_code = ClearenceCode(
                code=otp_value_str,
                created_by=parent,
                visitor_name=visitor_name,
                visitor_contact=visitor_contact,
                visitor_relationship=visitor_relationship,
                reason=reason,
                expiry_date=expiry_date,
                is_active=is_active,
                date_created=timezone.now(),
            )
            clearance_code.save()
            try:
                conn = http.client.HTTPSConnection("app.esmsuganda.com")
                headersList = {
                    "Accept": "*/*",
                    "Authorization": "Bearer ae7723e248188d5269bccbf2e88db4bb228d220eb47ecaa85bf287aaf6d081bcc595d962e8c842c857c04189277e6d5a",
                    "Content-Type": "application/json"
                }
                payload = json.dumps({
                    "number": visitor_contact,
                    "message": f"Your twinbrook temporary security code is {otp_value_str}, it expires on {expiry_date}",
                })
                conn.request("POST", "/api/v1/send-sms", payload, headersList)
                response = conn.getresponse()
                result = response.read()
            except:
                messages.error(request, 'There was an error sending the SMS but the clearance code was added successfully!')
                return render(request, 'user/Newcode.html')
            
            messages.success(request, 'Clearance Code added successfully and a code has been successfully sent to the user!')
            return redirect('new-clearance-code')
        
        except Exception as e:
            messages.error(request, 'There was an error adding the clearance code.')
            return render(request, 'user/Newcode.html')

    return render(request, 'user/Newcode.html')

def form_list_create(request):
    if request.method == 'POST':
        # Handle form creation
        form_name = request.POST.get('form_name')
        form_description = request.POST.get('form_description')
        class_teacher = request.POST.get('class_teacher')
        directions = request.POST.get('directions')

        # Create the new form
        form = Form(
            form_name=form_name,
            form_description=form_description,
            class_teacher=class_teacher,
            directions=directions
        )
        form.save()

        messages.success(request, 'Form created successfully!')
        return redirect('form_list_create')  # Redirect to the same page after form creation

    # Handle GET request: List all forms
    forms = Form.objects.all()
    return render(request, 'user/classes.html', {'forms': forms})

def delete_form(request, id):
    form = get_object_or_404(Form, id=id)
    if request.method == 'POST':
        form.delete()
        messages.success(request, 'Form deleted successfully!')
        return redirect('form_list')

def create_form(request):
    if request.method == "POST":
        form_name = request.POST.get('form_name')
        form_description = request.POST.get('form_description')
        class_teacher = request.POST.get('class_teacher')
        directions = request.POST.get('directions')

        new_form = Form(
            form_name=form_name,
            form_description=form_description,
            class_teacher=class_teacher,
            directions=directions,
        )
        new_form.save()
        messages.success(request, 'Form created successfully!')
        return redirect('form_list')  # Redirect to the form list page

    return render(request, 'user/create_form.html')