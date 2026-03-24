import random
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm, UpdateUserForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages


# База бурятских слов
BURYAD_WORDS = ['сайн', 'эжы', 'аба', 'баярлаха']


# Модель User (которая на самом деле MyUser)
User = get_user_model()


# Create your views here.


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name'].capitalize()
            user.last_name = form.cleaned_data['last_name'].capitalize()
            user.save()
            messages.success(request, 'Аккаунт успешно создан.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {'form': form})


def login(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Вы успешно вошли в аккаунт.')
                return redirect('profile')
            else:
                form.add_error(None, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, "users/login.html", {'form': form})


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')


@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        auth_logout(request)
        user.delete()
        messages.success(request, 'Аккаунт успешно удален.')
        return redirect('home')
    return redirect('profile')


@login_required
def profile(request):
    random_buryad_word = random.choice(BURYAD_WORDS)

    return render(request, "users/profile.html", context={
        'random_buryad_word': random_buryad_word,
    })


@login_required
def update_user(request):
    if request.method == 'POST':
        form = UpdateUserForm(data=request.POST, instance=request.user)
        if form.is_valid():
            if form.has_changed():
                user = form.save(commit=False)
                user.first_name = form.cleaned_data['first_name'].capitalize()
                user.last_name = form.cleaned_data['last_name'].capitalize()
                user.save()
                messages.success(request, 'Данные успешно изменены.')
                return redirect('profile')
            else:
                form.add_error(None, 'Вы не ввели никаких изменений.')
    else:
        form = UpdateUserForm(instance=request.user)

    return render(request, 'users/update_user.html', context={'form': form})


@login_required
def update_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен.')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/update_password.html', context={'form': form})
