import datetime
from datetime import timezone
import hashlib
import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User

from .models import Paste, AccessPeriod
from .forms import PasteForm, LoginForm, RegistrationForm


# Домашняя.
def home(request):
    return render(request, 'core_app/home.html')


# Добавление пасты.
def add_paste(request):
    # Если get-запрос.
    if request.method == 'GET':
        # Получение пустой формы.
        paste_form = PasteForm()

    # Если post-запрос.
    elif request.method == 'POST':
        # Получение формы из post-запроса.
        paste_form = PasteForm(request.POST)

        # Если форма валидна.
        if paste_form.is_valid():
            # Сохранение пасты.
            paste = paste_form.save()

            # Расчет даты и времени окончания доступности пасты. Если вынести в модель, то при изменеии даты и времени
            # доступности через админку будут неудобства. Оставляю здесь, так как задание тестовое.
            paste.access_time = datetime.datetime(2050, 1, 1, tzinfo=timezone.utc)
            if paste.access_period is not None:
                try:
                    access_period = AccessPeriod.objects.get(id=paste.access_period.id)
                except ObjectDoesNotExist as e:
                    pass
                else:
                    paste.access_time = datetime.datetime.now(timezone.utc) + datetime.timedelta(seconds=access_period.seconds)

            # Определение владельца пасты. Не выношу в модель, так как там нет инфомрации о сессии. Можно усложнить, но
            # не буду.
            if request.user.is_authenticated:
                paste.owner = request.user
            paste.save()

            # Редирект на просмотр пасты.
            return HttpResponseRedirect(reverse('core_app:paste', kwargs={'hash': paste.hash}))

    # Если ни get и ни post-запрос.
    else:
        return HttpResponse('invalid http request')

    return render(request, 'core_app/add_paste.html', {
        'paste_form': paste_form
    })


# Вывод пасты по хэшу.
def paste(request, hash):
    # Получение пасты по хэшу.
    try:
        paste = Paste.objects.get(hash=hash)

    # Паста не найдена.
    except ObjectDoesNotExist as e:
        return HttpResponseRedirect(reverse('core_app:oops'))

    # Если у пасты истек срок доступа.
    if paste.access_time < datetime.datetime.now(timezone.utc):
        return HttpResponseRedirect(reverse('core_app:oops'))

    # Если эта приватная паста и это не её владелец.
    if paste.private and request.user != paste.owner:
        return HttpResponseRedirect(reverse('core_app:oops'))

    return render(request, 'core_app/paste.html', {
        'paste': paste,
    })


# Паста не найдена или более недоступна.
def oops(request):
    return render(request, 'core_app/oops.html', status=404)


# Регистрация пользователя.
def registration(request):
    message = ''

    # Если get-запрос.
    if request.method == 'GET':
        # Формирование новой формы.
        registration_form = RegistrationForm()

    # Если post-запрос.
    elif request.method == 'POST':
        # Формирование формы из POST-данных.
        registration_form = RegistrationForm(request.POST)
        # Логин и пароль.
        username = request.POST['username']
        password = request.POST['password']

        # Поиск пользователя с указанным именем.
        try:
            User.objects.get(username=username)

        # Если пользователь с таким именем еще не зарегистрирован.
        except ObjectDoesNotExist as e:
            # Создание пользователя.
            user = User.objects.create_user(
                username=username,
                password=password
            )
            user.save()

            # Вход.
            auth_login(request, user)

            return HttpResponseRedirect(reverse('core_app:home'))

        message = 'Пользователь с таким именем уже зарегистрирован'

    # Если ни get-запрос и ни post-запрос.
    else:
        return HttpResponse('invalid http request')

    return render(request, 'core_app/registration.html', {
        'message': message,
        'registration_form': registration_form
    })


# Вход.
def login(request):
    message = ''

    # Если get-запрос.
    if request.method == 'GET':
        # # Формирование новой формы.
        login_form = LoginForm()

    # Если post-запрос.
    elif request.method == 'POST':
        # Формирование формы из POST-данных.
        login_form = LoginForm(request.POST)
        # Логин и пароль.
        username = request.POST['username']
        password = request.POST['password']

        # Аутентификация пользователя.
        user = authenticate(username=username, password=password)

        # Если форма валидна.
        if login_form.is_valid():
            # Если аутентификация пройдена.
            if user is not None:
                # Вход.
                auth_login(request, user)
                return HttpResponseRedirect(reverse('core_app:home'))

            message = 'Неверный логин или пароль'

    # Если ни get-запрос и ни post-запрос.
    else:
        return HttpResponse('invalid http request')

    return render(request, 'core_app/login.html', {
        'message': message,
        'login_form': login_form
    })


# Выход.
def logout(request):
    # Если пользователь аутентифицирован.
    if request.user.is_authenticated:
        auth_logout(request)

    return HttpResponseRedirect(reverse('core_app:home'))


# Список паст владельца.
def my_paste_list(request):
    # Если пользователь аутентифицирован.
    if request.user.is_authenticated:
        owner_paste_list = Paste.objects.filter(
            owner=request.user
        ).order_by('-id')

        paginator = Paginator(owner_paste_list, 3)
        page = request.GET.get('page')
        my_paste_list_paginator = paginator.get_page(page)

        return render(request, 'core_app/my_paste_list.html', {
            'my_paste_list_paginator': my_paste_list_paginator
        })

    return HttpResponseRedirect(reverse('core_app:access_denied'))


# Нет доступа.
def access_denied(request):
    return render(request, 'core_app/access_denied.html', status=403)


# Результат поискка.
def find(request):
    find_text = request.GET.get('text')

    # Поиск по тексту с учетом доступности по времени и публичности пасты.
    find_list = Paste.objects.filter(
        access_only_from_link=False,
        text__contains=find_text,
        access_time__gte=datetime.datetime.now(timezone.utc),
    ).order_by('-id')

    # Удаление из результатов поиска
    find_list_private_filter = []
    for paste in find_list:
        # Если это не приватная паста или она принадлежить текущему пользователю.
        if not paste.private or request.user == paste.owner:
            find_list_private_filter.append(paste)

    return render(request, 'core_app/find.html', {
        'find_text': find_text,
        'find_paste_list': find_list_private_filter,
    })
