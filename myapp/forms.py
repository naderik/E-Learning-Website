from django import forms
from django.contrib.auth.forms import UserCreationForm
from myapp.models import Order, Review, User, Student


class SearchForm(forms.Form):
    LENGTH_CHOICES = [
        (8, '8 Weeks'),
        (10, '10 Weeks'),
        (12, '12 Weeks'),
        (14, '14 Weeks'),
    ]
    name = forms.CharField(max_length=100, required=False, label='Student Name')
    length = forms.TypedChoiceField(widget=forms.RadioSelect, choices=LENGTH_CHOICES, coerce=int, required=False,
                                    label='Preferred course duration')
    max_price = forms.IntegerField(min_value=0, label='Maximum Price')


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['courses', 'student', 'order_status']
        widgets = {'courses': forms.CheckboxSelectMultiple(), 'order_type': forms.RadioSelect}
        labels = {'student': 'Student Name', }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['reviewer', 'course', 'rating', 'comments']
        widgets = {'course': forms.RadioSelect}
        labels = {'reviewer': 'please enter a valid Email', 'rating': 'Rating: An integer between 1 (worst) and 5 ('
                                                                      'best)', }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label='Username')
    password = forms.CharField(widget=forms.PasswordInput())


class RegisterForm(UserCreationForm):
    def _init_(self, *args, **kwargs):
        super(RegisterForm, self)._init_(*args, **kwargs)
        # do not require password confirmation
        del self.fields['password2']

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label='User Name')
