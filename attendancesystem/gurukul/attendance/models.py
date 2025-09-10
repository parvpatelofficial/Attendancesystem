from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Standard(models.Model):
    STANDARDS_CHOICES = [(str(i), f"Class {i}") for i in range(1, 11)]
    name = models.CharField(max_length=2, choices=STANDARDS_CHOICES)
    section = models.CharField(max_length=1, default='A')
    class Meta:
        ordering = ['name', 'section']
    def __str__(self):
        return f"Class {self.name}-{self.section}"
    
    name = models.CharField(max_length=2, choices=STANDARDS_CHOICES, unique=True)
    section = models.CharField(max_length=1, default='A')
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"Class {self.name}-{self.section}"

class Student(models.Model):
    roll_number = models.CharField(max_length=10)
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='students')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_contact = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    admission_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [['standard', 'roll_number']]
        ordering = ['standard__name', 'roll_number']

    def __str__(self):
        return f"{self.standard} – {self.roll_number} – {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class AttendanceRecord(models.Model):
    """Model for daily attendance records"""
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='absent')
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', 'student__roll_number']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"

class TeacherProfile(models.Model):
    """Extended profile for teachers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    assigned_standards = models.ManyToManyField(Standard, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"
