import datetime
from datetime import timezone
import hashlib
import random

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User


# Период доступности пасты.
class AccessPeriod(models.Model):
    text = models.CharField(max_length=32, verbose_name='Текст для периода доступности')
    seconds = models.IntegerField(verbose_name='Период доступности в секундах')
    # 10 минут 600
    # 1 час 3600
    # 3 часа 10800
    # 1 день 86400
    # 1 неделя 604800
    # 1 месяц 2419200
    # без ограничения NULL

    # Объект в строковом виде.
    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Период доступности пасты'
        verbose_name_plural = 'Периоды доступности пасты'


# ЯП.
class CodeLanguage(models.Model):
    name = models.CharField(max_length=32, verbose_name='Язык программирования')
    # php
    # javascript
    # html
    # python

    # Объект в строковом виде.
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Язык программирования'
        verbose_name_plural = 'Языки программирования'


# Паста.
class Paste(models.Model):
    text = models.TextField(max_length=65536, verbose_name='Текст пасты')
    access_period = models.ForeignKey(AccessPeriod, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Период доступности пасты')
    access_time = models.DateTimeField(null=True, verbose_name='Дата и время до которого доступна паста')
    access_only_from_link = models.BooleanField(default=False, verbose_name='Доступно только по ссылке')
    hash = models.CharField(max_length=32, verbose_name='Хэш пасты')

    code_language = models.ForeignKey(CodeLanguage, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Язык программирования')
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Владелец пасты')
    private = models.BooleanField(default=False, verbose_name='Приватная паста')

    # Объект в строковом виде.
    def __str__(self):
        return '{}: {}'.format(self.hash, self.text[0:32])

    # Сохранние записи.
    # TODO: реализовать через pre_save и receiver?
    def save(self, *args, **kwargs):
        # # Расчет даты и времени окончания доступности пасты.
        # self.access_time = datetime.datetime(2050, 1, 1, tzinfo=timezone.utc)
        # if self.access_period is not None:
        #     try:
        #         access_period = AccessPeriod.objects.get(id=self.access_period.id)
        #     except ObjectDoesNotExist as e:
        #         pass
        #     else:
        #         self.access_time = datetime.datetime.now(timezone.utc) + datetime.timedelta(seconds=access_period.seconds)

        # Расчет хеша для пасты.
        if not self.hash:
            # Источник хеша - текст пасты плюс случайное число.
            source = '{}{:0>8x}'.format(
                self.text,
                random.randint(0, 0xFFFFFFFF)
            )
            # Получение md5 хеша от источника.
            md5 = hashlib.md5()
            md5.update(source.encode("utf-8"))
            self.hash = md5.hexdigest()

        super(Paste, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Паста'
        verbose_name_plural = 'Пасты'
