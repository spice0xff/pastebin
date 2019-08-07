import datetime
from datetime import timezone
import logging
import hashlib

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, HttpResponse

from .models import Paste, AccessPeriod
from .forms import PasteForm


# Получение логера, определенного в settings.py
logger = logging.getLogger('debug')


# Домашняя.
def home(request):
    return render(request, 'core_app/home.html')


# Добавление пасты.
def add_paste(request):
    # Если get-запрос.
    if request.method == 'GET':
        logger.debug('request.GET: {}'.format(request.GET))

        # Получение пустой формы.
        paste_form = PasteForm()

    # Если post-запрос.
    elif request.method == 'POST':
        logger.debug('request.POST: {}'.format(request.POST))

        # Получение формы из post-запроса.
        paste_form = PasteForm(request.POST)

        logger.debug('errors: {}'.format(paste_form.errors))
        # Если форма валидна.
        if paste_form.is_valid():
            # Предаврительное сохранение формы.
            paste = paste_form.save(commit=False)

            # Расчет даты и времени окончания доступности пасты.
            access_period = AccessPeriod.objects.get(id=paste.access_period.id)
            paste.access_time = datetime.datetime.now(timezone.utc) + datetime.timedelta(seconds=access_period.seconds)
            # print('access_period: {}'.format(access_period.seconds))

            # Расчет хеща для пасты.
            paste.save()
            # Источник хеша - текст пасты плюс случайное число.
            # source = '{}{:0>8x}'.format(
            #     self.text,
            #     random.randint(0, 0xFFFFFFFF)
            # )
            # Источник хеша - id пасты.
            source = '{}'.format(paste.id, )
            # Получение md5 хеша от источника.
            md5 = hashlib.md5()
            md5.update(source.encode("utf-8"))
            paste.hash = md5.hexdigest()
            paste.save()

            # Редирект на просмотр пасты.
            return HttpResponseRedirect(reverse('core_app:paste', kwargs={'hash': paste.hash}))
        else:
            logger.debug('errors: {}'.format(paste_form.errors))

    # Если ни get и ни post-запрос.
    else:
        return HttpResponse('invalid http request')

    return render(request, 'core_app/add_paste.html', {
        'paste_form': paste_form
    })


# Вывод пасты по хэшу.
def paste(request, hash):
    logger.debug('paste()')
    logger.debug('hash: {}'.format(hash))

    # Получение пасты по хэшу.
    try:
        paste = Paste.objects.get(hash=hash)

    # Паста не найдена.
    except ObjectDoesNotExist as e:
        logger.warning('ObjectDoesNotExist: {}'.format(e))
        return HttpResponseRedirect(reverse('core_app:oops'))

    # print('paste.access_time: {}'.format(paste.access_time, ))
    # print('datetime.now(timezone.utc): {}'.format(datetime.datetime.now(timezone.utc), ))

    if paste.access_time < datetime.datetime.now(timezone.utc):
        return HttpResponseRedirect(reverse('core_app:oops'))

    return render(request, 'core_app/paste.html', {
        'paste': paste,
    })


# Паста не найдена или более недоступна.
def oops(request):
    return render(request, 'core_app/oops.html')
