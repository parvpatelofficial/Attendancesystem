from django import forms
from .models import Student, Standard

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True
        })
    )

class StudentForm(forms.ModelForm):
    standard = forms.ModelChoiceField(
        queryset=Standard.objects.all(),
        empty_label="Select Class",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Student
        fields = [
            'roll_number', 'first_name', 'last_name', 'standard',
            'date_of_birth', 'parent_contact', 'address'
        ]
        widgets = {
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'parent_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91-9876543210'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Student Address'
            }),
        }

    def clean_roll_number(self):
        roll = self.cleaned_data.get('roll_number')
        std  = self.cleaned_data.get('standard')
        if roll and std:
            qs = Student.objects.filter(roll_number=roll, standard=std)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f"Roll number {roll} already exists in {std}."
                )
        return roll
