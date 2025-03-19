from django import forms
from .models import Department, Employee, Role

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dept_name', 'description']

class RoleForm(forms.ModelForm):
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
    
    position = forms.ChoiceField(choices=POSITION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    ROLE_CHOICES = [
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
    
    role_name = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Role
        fields = ['role_name', 'position', 'description'] 

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'role_name': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
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

    position = forms.ChoiceField(
        choices=POSITION_CHOICES, 
        required=False,  # ✅ Make position optional
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,  # ✅ Make role optional
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Employee
        fields = [
            'first_name',
            'last_name',
            'username',
            'password',
            'email',
            'mobile',
            'department',
            'role',  
            'reporting_manager',  
            'date_of_joining',
            'position',
        ]

        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'reporting_manager': forms.Select(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(status=True)
        self.fields['role'].queryset = Role.objects.all()
        self.fields['reporting_manager'].queryset = Employee.objects.all()