from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Standard, Student, AttendanceRecord, TeacherProfile

@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'student_count']
    list_filter = ['name', 'section']
    search_fields = ['name']
    
    def student_count(self, obj):
        return obj.students.filter(is_active=True).count()
    student_count.short_description = 'Active Students'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'first_name', 'last_name', 'standard', 'is_active', 'admission_date']
    list_filter = ['standard', 'is_active', 'admission_date']
    search_fields = ['roll_number', 'first_name', 'last_name']
    list_editable = ['is_active']
    ordering = ['standard__name', 'roll_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('roll_number', 'first_name', 'last_name', 'standard')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'parent_contact', 'address')
        }),
        ('Academic Information', {
            'fields': ('admission_date', 'is_active')
        }),
    )

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by', 'created_at']
    list_filter = ['status', 'date', 'student__standard']
    search_fields = ['student__first_name', 'student__last_name', 'student__roll_number']
    date_hierarchy = 'date'
    ordering = ['-date', 'student__roll_number']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'marked_by')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'phone']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    filter_horizontal = ['assigned_standards']

# Customize User admin to show teacher profiles
class TeacherInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Teacher Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (TeacherInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize admin site headers
admin.site.site_header = "Gurukul Attendance System"
admin.site.site_title = "Gurukul Admin"
admin.site.index_title = "Welcome to Gurukul Administration"
