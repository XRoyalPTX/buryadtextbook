from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(label=_("Логин"))
    password = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    username = forms.CharField(label=_("Логин"), required=True)
    first_name = forms.CharField(label=_("Имя"), required=True)
    last_name = forms.CharField(label=_("Фамилия"), required=True)
    email = forms.EmailField(label=_("Электронная почта"), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop('autofocus', None)

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("Пользователь с таким никнеймом уже существует."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Пользователь с такой электронной почтой уже существует."))
        return email


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        query = User.objects.filter(username__iexact=username)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise forms.ValidationError(_("Пользователь с таким никнеймом уже существует."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        query = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise forms.ValidationError(_("Пользователь с такой электронной почтой уже существует."))
        return email
