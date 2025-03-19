from django.db import models
from django.contrib.auth.models import User

# Department Model
class Department(models.Model):
    dept_id = models.AutoField(primary_key=True, unique=True)
    dept_name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.dept_name

    def has_linked_employees(self):
        """Check if there are any employees linked to this department"""
        return self.employee_set.exists()

    def reactivate(self):
        """Reactivate a deactivated department"""
        if not self.status:
            self.status = True
            self.save()
            return True
        return False

    class Meta:
        db_table = 'department'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'


# Role Model
class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.role_name

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'


# Employee Model (Unified)
class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    status = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  
    first_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='role_employees')
    reporting_manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reporting_employees'
    )
    
    # ✅ FIX: Change position to CharField instead of ForeignKey
    POSITION_CHOICES = [
        ('', 'Select a position'),
        ('Accountant', 'Accountant'),
        ('Analyst', 'Analyst'),
        ('Developer', 'Developer'),
        ('Designer', 'Designer'),
        ('Engineer', 'Engineer'),
        ('Manager', 'Manager'),
        ('Specialist', 'Specialist'),
        ('Technician', 'Technician'),
    ]
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, null=True, blank=True)

    date_of_joining = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'employee'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'


# Task Model
class Task(models.Model):
    TASK_PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]
    TASK_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Team', 'Team')
    ]

    task_id = models.AutoField(primary_key=True)
    task_title = models.CharField(max_length=100, help_text="The title of the task")
    task_description = models.CharField(max_length=300, help_text="A brief description of the task")
    task_priority = models.CharField(max_length=200, choices=TASK_PRIORITY_CHOICES, default='Medium',
                                     help_text="The priority level of the task")
    start_date = models.DateField(help_text="The start date of the task")
    end_date = models.DateField(help_text="The end date of the task")
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, default='Individual',
                                 help_text="The type of task (Individual or Team)")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date the task was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date the task was last updated")

    def __str__(self):
        return self.task_title


# Task Assignment Model
class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]

    assignment_id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments',
                             help_text="The task being assigned")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tasks',
                                 help_text="The employee to whom the task is assigned")
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_assigned',
                                    help_text="The user who assigned the task")
    assigned_date = models.DateTimeField(auto_now_add=True, help_text="The date the task was assigned")
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Pending',
                              help_text="The current status of the task")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="The date the task was completed")

    def __str__(self):
        return f"{self.task.task_title} - {self.employee.user.username}"
