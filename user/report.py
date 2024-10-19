from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Attendance, User  # Adjust import according to your models

def reports(request, user_id=None):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = None

    if start_date_str and end_date_str:
        # If dates are provided, filter by date range
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        
        # Filter attendance
        if user:
            attendance = Attendance.objects.filter(user=user, date__range=[start_date, end_date])
        else:
            attendance = Attendance.objects.filter(date__range=[start_date, end_date])
        
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

        # Prepare data for chart
        chart_data = {
            "labels": ["Attended", "Missed"],
            "data": [sum(attendance_dict.values()), missed_days]
        }
        
        return render(request, 'user/reports.html', {
            'attendance': attendance,
            'chart_data': chart_data,
            'start_date': start_date,
            'end_date': end_date,
            'user': user
        })
    else:
        # If no filters applied, show the full table
        if user:
            attendance = Attendance.objects.filter(user=user)
        else:
            attendance = Attendance.objects.all()
            
        return render(request, 'user/reports.html', {
            'attendance': attendance,
            'chart_data': None,  # No chart data when no filter is applied
            'start_date': None,
            'end_date': None,
            'user': user
        })
