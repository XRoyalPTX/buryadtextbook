from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm, UpdateUserForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from courses.models import LessonProgress, CourseProgress, Lesson
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.db import transaction
import logging
from django.conf import settings

# Модель User (которая на самом деле MyUser)
User = get_user_model()


# Create your views here.

logger = logging.getLogger(__name__)

def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.first_name = form.cleaned_data['first_name'].capitalize()
                    user.last_name = form.cleaned_data['last_name'].capitalize()
                    
                    user.is_active = False
                    user.save() 

                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    protocol = 'https' if request.is_secure() else 'http'
                    current_site = request.get_host()
                    activation_url = f"{protocol}://{current_site}/auth/activate/{uid}/{token}/"
                    
                    subject = _("Активация аккаунта Сэсэн")
                    message = _(
                        "Сайн байна! Спасибо за регистрацию на платформе Сэсэн.\n\n"
                        "Для подтверждения вашего Email и активации профиля перейдите по ссылке:\n"
                        "%(activation_url)s\n\n"
                        "Ссылка действительна в течение 3 дней."
                    ) % {'activation_url': activation_url}
                    
                    send_mail(
                        subject, 
                        message, 
                        settings.DEFAULT_FROM_EMAIL, 
                        [user.email],
                        fail_silently=False 
                    )
                
                return render(request, 'registration/activation_sent.html')
                
            except Exception as e:
                logger.error(f"Ошибка при регистрации пользователя: {e}")
                form.add_error(None, _("Не удалось отправить письмо с активацией. Пожалуйста, проверьте правильность Email или попробуйте позже."))
    else:
        form = RegisterForm()
        
    return render(request, "users/register.html", {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True 
        user.save()
        messages.success(request, _('Ваш аккаунт успешно активирован. Теперь вы можете войти.'))
        return redirect('login')
    else:
        return render(request, 'registration/activation_invalid.html')


def change_email(request, uidb64, token, encoded_email):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        new_email = force_str(urlsafe_base64_decode(encoded_email))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        new_email = None

    if user is not None and new_email and default_token_generator.check_token(user, token):
        if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
            messages.error(request, _('Данный адрес электронной почты уже используется другим пользователем.'))
            return redirect('profile')
        user.email = new_email
        user.save(update_fields=['email'])
        messages.success(request, _('Email успешно изменен.'))
        return redirect('profile')
    else:
        return render(request, 'registration/activation_invalid.html')


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
                messages.success(request, _('Вы успешно вошли в аккаунт.'))
                return redirect('profile')
            else:
                form.add_error(None, _('Неверный логин или пароль'))
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
        messages.success(request, _('Аккаунт успешно удален.'))
        return redirect('home')
    return redirect('profile')


@login_required
def profile(request):
    num_of_lessons = LessonProgress.objects.filter(
        user = request.user,
        complete_date__isnull=False,
    ).count()

    user_course_progresses = CourseProgress.objects.filter(
        user = request.user,
    )

    today = timezone.now().date()

    if request.user.last_activity_date < today - timedelta(days=1):
        if request.user.streak_count != 0:
            request.user.streak_count = 0
            request.user.save(update_fields=['streak_count'])

    for progress in user_course_progresses:
        course = progress.course
        total_lessons = Lesson.objects.filter(course=course, is_published=True).count()
        progress.total_lessons = Lesson.objects.filter(course=course, is_published=True).count()
        
        completed_lessons = LessonProgress.objects.filter(
            user=request.user, 
            lesson__course=course, 
            complete_date__isnull=False
        ).count()

        progress.completed_lessons = LessonProgress.objects.filter(
            user=request.user, 
            lesson__course=course, 
            complete_date__isnull=False
        ).count()

        if total_lessons > 0:
            progress.percent = int((completed_lessons / total_lessons) * 100)
        else:
            progress.percent = 0

    return render(request, "users/profile.html", context={
        'num_of_lessons': num_of_lessons,
        'user_course_progresses': user_course_progresses,
        'streak_last_digit': request.user.streak_count % 10,
        'streak_last_two': request.user.streak_count % 100,
    })


@login_required
def update_user(request):
    if request.method == 'POST':
        form = UpdateUserForm(data=request.POST, instance=request.user)
        if form.is_valid():
            if form.has_changed():

                if 'email' in form.changed_data:
                    new_email = form.cleaned_data['email']
                    
                    token = default_token_generator.make_token(request.user)
                    uid = urlsafe_base64_encode(force_bytes(request.user.pk))
                    encoded_email = urlsafe_base64_encode(force_bytes(new_email))
                    
                    protocol = 'https' if request.is_secure() else 'http'
                    current_site = request.get_host()
                    
                    activation_url = f"{protocol}://{current_site}/auth/change-email/{uid}/{token}/{encoded_email}/"
                    
                    subject = _("Подтверждение смены Email на Сэсэн")
                    message = _(
                        "Сайн байна, %(first_name)s!\n\n"
                        "Вы запросили изменение адреса электронной почты на платформе Сэсэн.\n"
                        "Для подтверждения нового Email перейдите по ссылке:\n"
                        "%(activation_url)s\n\n"
                        "Если вы не совершали данного действия, просто проигнорируйте это письмо. "
                        "Ваш аккаунт останется привязан к старому адресу."
                    ) % {'first_name': request.user.first_name, 'activation_url': activation_url}
                    
                    try:
                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_email], fail_silently=False)
                        
                        user = form.save(commit=False)
                        user.first_name = form.cleaned_data['first_name'].capitalize()
                        user.last_name = form.cleaned_data['last_name'].capitalize()
                        user.email = request.user._meta.model.objects.get(pk=request.user.pk).email
                        user.save()
                        
                        messages.info(request, _('На вашу новую почту отправлено письмо со ссылкой для подтверждения.'))
                        return redirect('profile')
                    except Exception as e:
                        form.add_error(None, _('Ошибка отправки письма. Попробуйте позже.'))
                else:
                    user = form.save(commit=False)
                    user.first_name = form.cleaned_data['first_name'].capitalize()
                    user.last_name = form.cleaned_data['last_name'].capitalize()
                    user.save()
                    messages.success(request, _('Данные успешно изменены.'))
                    return redirect('profile')
            else:
                form.add_error(None, _('Вы не ввели никаких изменений.'))
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
            messages.success(request, _('Пароль успешно изменен.'))
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/update_password.html', context={'form': form})
