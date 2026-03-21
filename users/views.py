import random
import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


# База бурятских слов
BURYAD_WORDS = ['сайн', 'эжы', 'аба', 'баярлаха']


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
        return redirect('home')
    return redirect('profile')


@login_required
def profile(request):
    russian_translations = []
    random_buryad_word = random.choice(BURYAD_WORDS)

    url = f"https://burlang.ru/api/v1/buryat-word/translate?q={random_buryad_word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        translations_list = data.get('translations')
        if translations_list:
            for russian_translation in translations_list:
                russian_translations.append(russian_translation.get('value'))
        else:
            russian_translations = 'Перевод этого слова ещё не добавлен.'
    else:
        russian_translations = 'Сервер не отвечает.'
    print(russian_translations)

    return render(request, "users/profile.html", context={
        'random_buryad_word': random_buryad_word,
        'russian_translations': russian_translations,
    })
