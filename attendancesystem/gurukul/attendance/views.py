from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Student, Standard, AttendanceRecord, TeacherProfile
from .forms import StudentForm, LoginForm
import json

def login_view(request):
    """Teacher login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'attendance/login.html', {'form': form})

@login_required
def logout_view(request):
    """Teacher logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    """Main dashboard view"""
    today = timezone.now().date()
    
    # Get all standards
    standards = Standard.objects.all()
    
    # Get today's attendance summary
    attendance_summary = []
    for standard in standards:
        total_students = standard.students.filter(is_active=True).count()
        present_today = AttendanceRecord.objects.filter(
            student__standard=standard,
            date=today,
            status='present'
        ).count()
        
        attendance_summary.append({
            'standard': standard,
            'total_students': total_students,
            'present_today': present_today,
            'absent_today': total_students - present_today,
            'percentage': round((present_today / total_students * 100) if total_students > 0 else 0, 1)
        })
    
    # Recent attendance records
    recent_records = AttendanceRecord.objects.filter(
        date__gte=today - timedelta(days=7)
    ).select_related('student', 'student__standard').order_by('-created_at')[:10]
    
    context = {
        'attendance_summary': attendance_summary,
        'recent_records': recent_records,
        'today': today,
        'total_standards': standards.count(),
        'total_students': Student.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'attendance/dashboard.html', context)

@login_required
def take_attendance(request, standard_id=None):
    """Take attendance for a specific standard"""
    standards = Standard.objects.all()
    selected_standard = None
    students = []
    today = timezone.now().date()
    
    if standard_id:
        selected_standard = get_object_or_404(Standard, id=standard_id)
        students = selected_standard.students.filter(is_active=True).order_by('roll_number')
        
        # Get existing attendance for today
        existing_attendance = AttendanceRecord.objects.filter(
            student__standard=selected_standard,
            date=today
        )
        
        attendance_dict = {record.student.id: record.status for record in existing_attendance}
        
        # Add current attendance status to students
        for student in students:
            student.current_status = attendance_dict.get(student.id, 'absent')
    
    if request.method == 'POST':
        if selected_standard:
            attendance_data = request.POST.get('attendance_data')
            if attendance_data:
                try:
                    attendance_dict = json.loads(attendance_data)
                    
                    for student_id, status in attendance_dict.items():
                        student = get_object_or_404(Student, id=student_id)
                        
                        # Update or create attendance record
                        attendance_record, created = AttendanceRecord.objects.update_or_create(
                            student=student,
                            date=today,
                            defaults={
                                'status': status,
                                'marked_by': request.user,
                            }
                        )
                    
                    messages.success(request, f'Attendance saved successfully for Class {selected_standard.name}!')
                    return redirect('dashboard')
                
                except json.JSONDecodeError:
                    messages.error(request, 'Invalid attendance data.')
    
    context = {
        'standards': standards,
        'selected_standard': selected_standard,
        'students': students,
        'today': today,
    }
    
    return render(request, 'attendance/take_attendance.html', context)

@login_required
def view_attendance(request):
    """View attendance records with filters"""
    standards = Standard.objects.all()
    students = Student.objects.filter(is_active=True)
    
    # Get filter parameters
    standard_id = request.GET.get('standard')
    student_id = request.GET.get('student')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Build query
    attendance_records = AttendanceRecord.objects.all().select_related('student', 'student__standard')
    
    if standard_id:
        attendance_records = attendance_records.filter(student__standard_id=standard_id)
        students = students.filter(standard_id=standard_id)
    
    if student_id:
        attendance_records = attendance_records.filter(student_id=student_id)
    
    if start_date:
        attendance_records = attendance_records.filter(date__gte=start_date)
    
    if end_date:
        attendance_records = attendance_records.filter(date__lte=end_date)
    
    attendance_records = attendance_records.order_by('-date', 'student__roll_number')
    
    context = {
        'attendance_records': attendance_records,
        'standards': standards,
        'students': students,
        'filters': {
            'standard_id': standard_id,
            'student_id': student_id,
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    
    return render(request, 'attendance/view_attendance.html', context)

@login_required
def add_student(request):
    """Add new student"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name} added successfully!')
            return redirect('manage_students')
    else:
        form = StudentForm()
    
    return render(request, 'attendance/add_student.html', {'form': form})

@login_required
def manage_students(request):
    """Manage all students"""
    standard_id = request.GET.get('standard')
    search = request.GET.get('search')
    
    students = Student.objects.filter(is_active=True).select_related('standard')
    
    if standard_id:
        students = students.filter(standard_id=standard_id)
    
    if search:
        students = students.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(roll_number__icontains=search)
        )
    
    students = students.order_by('standard__name', 'roll_number')
    standards = Standard.objects.all()
    
    context = {
        'students': students,
        'standards': standards,
        'current_standard': standard_id,
        'search_query': search,
    }
    
    return render(request, 'attendance/manage_students.html', context)

@login_required
def edit_student(request, student_id):
    """Edit student information"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name} updated successfully!')
            return redirect('manage_students')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'attendance/add_student.html', {
        'form': form,
        'student': student,
        'edit_mode': True
    })

@login_required
def delete_student(request, student_id):
    """Soft delete student (mark as inactive)"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student.is_active = False
        student.save()
        messages.success(request, f'Student {student.full_name} has been removed.')
        return redirect('manage_students')
    
    return render(request, 'attendance/confirm_delete.html', {'student': student})
