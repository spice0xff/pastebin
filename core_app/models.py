import random
import hashlib

from django.db import models


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
    # без ограничения 1576800000 (50 лет)

    # Объект в строковом виде.
    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Период доступности пасты'
        verbose_name_plural = 'Периоды доступности пасты'


# Паста.
class Paste(models.Model):
    text = models.TextField(max_length=65536, verbose_name='Текст пасты')
    access_period = models.ForeignKey(AccessPeriod, on_delete=models.PROTECT, verbose_name='Период доступности пасты')
    access_time = models.DateTimeField(verbose_name='Дата и время до которого доступна паста')
    access_only_from_link = models.BooleanField(default=False, verbose_name='Доступно только по ссылке')
    hash = models.CharField(max_length=32, verbose_name='Хэш пасты')

    # Объект в строковом виде.
    def __str__(self):
        return '{}: {}'.format(self.hash, self.text[0:32])

    # # Сохранние записи.
    # # TODO: реализовать через pre_save и receiver?
    # def save(self, *args, **kwargs):
    #     # Текст пасты плюс случайное число.
    #     source = '{}{:0>8x}'.format(
    #         self.text,
    #         random.randint(0, 0xFFFFFFFF)
    #     )
    #
    #     # Получение md5 хеша от текста пасты плюс случайное число.
    #     md5 = hashlib.md5()
    #     md5.update(source.encode("utf-8"))
    #     self.hash = md5.hexdigest()
    #
    #     super(Paste, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Паста'
        verbose_name_plural = 'Пасты'
