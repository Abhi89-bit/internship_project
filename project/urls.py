from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from app import views
from app.views import task_dashboard

urlpatterns = [
    path('', RedirectView.as_view(url='departments/')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Department URLs
    path('departments/', include('app.urls')),
    path('reactivate/<int:dept_id>/', views.reactivate_department, name='reactivate_department'),

    # Role URLs
    path('roles/', views.role_dashboard, name='role_dashboard'),
    path('roles/reactivate/<int:role_id>/', views.reactivate_role, name='reactivate_role'),
    path('roles/create/', views.create_role, name='create_role'),
    path('roles/update/<int:role_id>/', views.update_role, name='update_role'),
    path('roles/delete/<int:role_id>/', views.delete_role, name='delete_role'),

    # Employee URLs
    path('employees/', views.employee_dashboard, name='employee_dashboard'),
    path('employees/create/', views.create_employee, name='create_employee'),
    path('employees/update/<int:emp_id>/', views.update_employee, name='update_employee'),
    path('employees/delete/<int:emp_id>/', views.delete_employee, name='delete_employee'),

    #Task URLs
    path('dashboard/', task_dashboard, name='task_dashboard'),
    path('create/', views.create_task, name='create_task'),
    path('update/<int:assignment_id>/', views.update_task, name='update_task'),
    path('delete/<int:assignment_id>/', views.delete_task, name='delete_task'),
    path('task/<int:assignment_id>/', views.task_detail, name='task_detail'), 
]
