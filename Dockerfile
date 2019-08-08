# Из python-образа.
FROM python

# Клонирование репозитория с github.com.
RUN git clone https://github.com/spice0xff/pastebin ~/pastebin

# Обновление pip.
RUN pip install --upgrade pip

# Установка необхоидмых зависимостей.
RUN pip install -r ~/pastebin/requirements.txt

# Создание файла миграции.
RUN python ~/pastebin/manage.py makemigrations core_app

# Создание БД.
RUN python ~/pastebin/manage.py migrate

# Заполнение БД.
RUN python ~/pastebin/manage.py loaddata init.json
