from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms




class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length = 50)
    last_name = forms.CharField(max_length = 70)
    old = forms.IntegerField(max_value=100)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'old', 'email', 'password1', 'password2')