from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    path('take-attendance/<int:standard_id>/', views.take_attendance, name='take_attendance_standard'),
    path('view-attendance/', views.view_attendance, name='view_attendance'),
    path('add-student/', views.add_student, name='add_student'),
    path('manage-students/', views.manage_students, name='manage_students'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
]
