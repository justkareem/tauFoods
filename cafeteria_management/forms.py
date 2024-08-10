from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'id': 'floatingInput',
        'placeholder': 'Email Address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'id': 'floatingInput1',
        'placeholder': 'Password'
    }))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input input-primary',
        'id': 'customCheck1'
    }))


class FoodForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'floatingInput',
        'placeholder': 'Food Title'
    }))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'id': 'floatingInput',
        'placeholder': 'Price'
    }))
    img = forms.ImageField(widget=forms.ClearableFileInput(attrs={
        'class': 'form-control',
    }))


class AnnouncementForm(forms.Form):
    title = forms.CharField(
        label='Title',
        max_length=100,
        required=False,  # Title is not required
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Notification Title',
            'aria-describedby': 'titleHelp'
        })
    )
    content = forms.CharField(
        label='Content',
        max_length=500,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Notification Content'
        })
    )
