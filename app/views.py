from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from app.models import Department, Employee, Role , Task, TaskAssignment
from .forms import DepartmentForm, EmployeeForm, RoleForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from django.core.paginator import Paginator  
from django.utils import timezone
from django.contrib.auth.models import User



class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

def is_admin(user):
    return user.is_superuser

# Role views
@login_required
@user_passes_test(is_admin)
def role_dashboard(request):
    all_roles = Role.objects.all()  # Fetch all roles
    active_roles = all_roles.filter(status=True)  # Filter active roles
    inactive_roles = all_roles.filter(status=False)  # Filter inactive roles

    return render(request, 'roles/dashboard.html', {
        'active_roles': active_roles,
        'inactive_roles': inactive_roles
    })

@login_required
@user_passes_test(is_admin)
def create_role(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            # Include the selected position in the role name
            position = form.cleaned_data.get('position')  # Get the selected position
            role_name = form.cleaned_data.get('role_name')  # Get the role name
            form.instance.role_name = f"{role_name} ({position})" if position else role_name
            form.save()
            messages.success(request, 'Role created successfully!')
            return redirect('role_dashboard')
        else:
            # Log form errors
            print(form.errors)  # Log the errors to the console for debugging
    else:
        form = RoleForm()
    return render(request, 'roles/form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def update_role(request, role_id):
    role = get_object_or_404(Role, role_id=role_id)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            position = form.cleaned_data.get('position')  
            role_name = form.cleaned_data.get('role_name')  
            form.instance.role_name = f"{role_name} ({position})" if position else role_name
            form.save()
            messages.success(request, 'Role updated successfully!')
            return redirect('role_dashboard')
    else:
        form = RoleForm(instance=role)
    return render(request, 'roles/form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_role(request, role_id):
    role = get_object_or_404(Role, role_id=role_id)
    if request.method == 'POST':
        role.status = False  # Soft delete
        role.save()
        messages.success(request, 'Role deleted successfully!')
        return redirect('role_dashboard')
    return render(request, 'roles/confirm_delete.html', {'role': role})

@login_required
@user_passes_test(is_admin)
def department_dashboard(request):
    active_departments = Department.objects.filter(status=True)
    inactive_departments = Department.objects.filter(status=False)
    return render(request, 'departments/dashboard.html', {
        'active_departments': active_departments,
        'inactive_departments': inactive_departments
    })

@login_required
@user_passes_test(is_admin)
def create_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully!')
            return redirect('departments:dashboard')
    else:
        form = DepartmentForm()
    return render(request, 'departments/form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def update_department(request, dept_id):
    department = get_object_or_404(Department, dept_id=dept_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('departments:dashboard')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'departments/form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def reassign_employees(request, dept_id):
    department = get_object_or_404(Department, dept_id=dept_id)
    employees = Employee.objects.filter(department=department)
    
    if request.method == 'POST':
        new_department_id = request.POST.get('new_department')
        new_department = get_object_or_404(Department, dept_id=new_department_id)
        
        employees.update(department=new_department)
        messages.success(request, f'Employees successfully reassigned to {new_department.dept_name}')
        return redirect('departments:delete', dept_id=dept_id)
    
    departments = Department.objects.filter(status=True).exclude(dept_id=department.dept_id)

    return render(request, 'departments/reassign_employees.html', {
        'department': department,
        'employees': employees,
        'departments': departments
    })

@login_required
@user_passes_test(is_admin)
def reactivate_department(request, dept_id):
    """Reactivate a deactivated department"""
    department = get_object_or_404(Department, dept_id=dept_id)
    
    if department.reactivate():
        messages.success(request, f"Department '{department.dept_name}' has been reactivated successfully.")
    else:
        messages.warning(request, f"Department '{department.dept_name}' is already active.")
    
    return redirect('departments:dashboard')

@login_required
@user_passes_test(is_admin)
def delete_department(request, dept_id):
    department = get_object_or_404(Department, dept_id=dept_id)
    if request.method == 'POST':
        # Debugging messages to log the status and linked employees
        print(f"Department Status: {department.status}")
        print(f"Linked Employees Count: {department.employee_set.filter(status=True).count()}")

        if department.has_linked_employees():
            messages.error(request, 
                'Cannot deactivate department. There are active employees linked to this department. Please reassign them to another department first using the Employee Management section.' 
            )

        else:
            department.status = False
            department.save()
            messages.success(request, f'Department "{department.dept_name}" has been deactivated successfully!')

        return redirect('departments:dashboard')
    
    # Render the confirmation page
    return render(request, 'departments/confirm_delete.html', {
        'department': department,
        'has_linked_employees': department.has_linked_employees(),
        'linked_employee_count': department.employee_set.count()
    })

@login_required
@user_passes_test(is_admin)
def search_department(request):
    query = request.GET.get('q')
    if query:
        departments = Department.objects.filter(
            dept_name__icontains=query, 
            status=True
        )
    else:
        departments = Department.objects.filter(status=True)
    return render(request, 'departments/search_results.html', {'departments': departments})

@login_required
@user_passes_test(is_admin)
def view_role(request, role_id):
    role = get_object_or_404(Role, role_id=role_id)
    return render(request, 'roles/view.html', {'role': role})

@login_required
@user_passes_test(is_admin)
def reactivate_role(request, role_id):
    role = get_object_or_404(Role, role_id=role_id)
    role.status = True  # Reactivate the role
    role.save()
    messages.success(request, f"Role '{role.role_name}' has been reactivated successfully.")
    return redirect('role_dashboard')

@login_required
@user_passes_test(is_admin)
def employee_dashboard(request):
    employees = Employee.objects.all()
    return render(request, 'employees/dashboard.html', {'employees': employees})

@login_required
@user_passes_test(is_admin)
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee created successfully!')
            return redirect('employee_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")  
    else:
        form = EmployeeForm()

    return render(request, 'employees/form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def update_employee(request, emp_id):
    employee = get_object_or_404(Employee, employee_id=emp_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_dashboard')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_employee(request, emp_id):
    employee = get_object_or_404(Employee, employee_id=emp_id)  
    if request.method == 'POST':
        employee.delete()  
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employee_dashboard')
    return render(request, 'employees/confirm_delete.html', {'employee': employee})

@login_required
@user_passes_test(is_admin)
def view_department_employees(request, dept_id):
    """View employees in a specific department"""
    department = get_object_or_404(Department, dept_id=dept_id)
    employees = Employee.objects.filter(department=department)  
    
    return render(request, 'departments/view_employees.html', {
        'department': department,
        'employees': employees
    })

#task view
@login_required
def task_detail(request, assignment_id):
    task = get_object_or_404(Task, task_id=assignment_id)  # Ensure task_id is correct

    # Define the context dictionary
    context = {
        'task': task
    }

    return render(request, 'task/task_detail.html', context)


@login_required
def task_dashboard(request):

    # Handle marking a task as completed
    if request.method == "POST" and 'mark_completed' in request.POST:
        assignment_id = request.POST.get('assignment_id')
        assignment = get_object_or_404(TaskAssignment, assignment_id=assignment_id)
        if assignment.employee.user == request.user or request.user.is_superuser or request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists():
            assignment.status = 'Completed'
            assignment.completed_at = timezone.now()
            assignment.save()
            messages.success(request, f"Task '{assignment.task.task_title}' marked as completed.")

    # Task filtering based on user role
    if request.user.is_superuser:  # Admins see all tasks
        tasks = TaskAssignment.objects.all()
    elif request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists():  # Team Leaders/Managers see their assigned tasks or tasks assigned to them
        tasks = TaskAssignment.objects.filter(assigned_by=request.user) | TaskAssignment.objects.filter(employee__user=request.user)
    else:  # Employees see only tasks assigned to them
        tasks = TaskAssignment.objects.filter(employee__user=request.user)

    # Apply filters
    employee_filter = request.GET.get('employee')
    status_filter = request.GET.get('status')
    start_date_from = request.GET.get('start_date_from')
    start_date_to = request.GET.get('start_date_to')

    if employee_filter and request.user.is_superuser:  # Admin-only filter
        tasks = tasks.filter(employee__user__username=employee_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if start_date_from and start_date_to:
        tasks = tasks.filter(task__start_date__range=[start_date_from, start_date_to])

    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_tasks = tasks.count()
    completed = tasks.filter(status='Completed').count()
    pending = tasks.filter(status='Pending').count()
    in_progress = tasks.filter(status='In Progress').count()

    # Employees for filter (admin-only)
    employees = User.objects.filter(employee__employee_id__isnull=False).exclude(id=request.user.id) if request.user.is_superuser else []

    context = {
        'page_obj': page_obj,
        'stats': {'total': total_tasks, 'completed': completed, 'pending': pending, 'in_progress': in_progress},
        'employees': employees,
        'is_admin': request.user.is_superuser,
    }
    return render(request, 'task/task_dashboard.html', context)


@login_required
def create_task(request):
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists()):
        messages.error(request, "You do not have permission to create tasks.")
        return redirect('task:dashboard')

    if request.method == 'POST':
        try:
            task = Task.objects.create(
                task_title=request.POST['task_title'],
                task_description=request.POST['task_description'],
                task_priority=request.POST['task_priority'],
                start_date=request.POST['start_date'],
                end_date=request.POST['end_date'],
                task_type=request.POST['task_type'],
            )
            employee = Employee.objects.get(user__username=request.POST['assigned_to'])
            TaskAssignment.objects.create(
                task=task,
                employee=employee,
                assigned_by=request.user,
            )
            messages.success(request, 'Task created successfully!')
            return redirect('task:dashboard')
        except Employee.DoesNotExist:
            messages.error(request, 'Selected employee does not exist.')
        except Exception as e:
            messages.error(request, f'Error creating task: {str(e)}')

    if request.user.is_superuser:
        employees = Employee.objects.all().values_list('user__username', flat=True)
    else:
        employees = Employee.objects.filter(
            profile_manager_user=request.user
        ).values_list('user__username', flat=True)

    return render(request, 'task/create_task.html', {'employees': employees})

@login_required
def update_task(request, assignment_id):
    assignment = get_object_or_404(TaskAssignment, assignment_id=assignment_id)

    # Restrict updates to the assigned_by user, Admin, or authorized roles
    if not (request.user == assignment.assigned_by or request.user.is_superuser or request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists()):
        messages.error(request, "You do not have permission to update this task.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            assignment.task.task_title = request.POST['task_title']
            assignment.task.task_description = request.POST['task_description']
            assignment.task.task_priority = request.POST['task_priority']
            assignment.task.start_date = request.POST['start_date']
            assignment.task.end_date = request.POST['end_date']
            assignment.task.task_type = request.POST['task_type']
            assignment.employee = Employee.objects.get(user__username=request.POST['assigned_to'])
            assignment.status = request.POST['status']
            assignment.task.save()
            assignment.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('dashboard')
        except Employee.DoesNotExist:
            messages.error(request, 'Selected employee does not exist.')
        except Exception as e:
            messages.error(request, f'Error updating task: {str(e)}')

    # Fetch Employee objects for the dropdown
    if request.user.is_superuser:
        employees = Employee.objects.all()  # Admins see all employees
    elif request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists():
        employees = Employee.objects.filter(profile_manager_user=request.user)  # Employees under this manager
    else:
        employees = []  # Regular employees can't reassign tasks

    context = {
        'assignment': assignment,
        'employees': employees,
    }
    return render(request, 'task/update_task.html', context)
@login_required
def delete_task(request, assignment_id):
    assignment = get_object_or_404(TaskAssignment, assignment_id=assignment_id)  # Ensure the correct model reference

    # Restrict deletion to the assigned_by user, Admin, or authorized roles
    if not (request.user == assignment.assigned_by or request.user.is_superuser or request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists()):
        messages.error(request, "You do not have permission to delete this task.")
        return redirect('task_dashboard')  # Ensure correct redirect

    if request.method == 'POST':
        assignment.delete()  # Directly delete the TaskAssignment object
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_dashboard')  # Ensure correct redirect

    return render(request, 'task/delete_task.html', {'assignment': assignment})
