# `Foodgram` - сайт 'Продуктовый помощник'
#### О проекте:
 Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
 

## Технологии в проекте<br>
🔹 Python<br>
🔹 Django<br>
🔹 Django REST Framework<br>
🔹 PostgreSQL<br>
🔹 Nginx<br>
🔹 Gunicorn<br>
🔹 Docker<br>

## Подготовка и запуск проекта

- Выполните вход на свой удаленный сервер:
```
ssh username@ip
```
- Установите docker и docker-compose на сервер:
```
sudo apt install docker.io 
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

```

- Клонируйте репозиторий командой:
```
git clone https://github.com/oitczvovich/foodgram-project-react
``` 
- Перейдите в каталог командой:
```
cd foodgram-project-react/infra
```
- Создаем файл .env с переменными окружения:
```
SECRET_KEY='<ключ>'
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя_БД>
POSTGRES_USER=<имя_пользователя>
POSTGRES_PASSWORD=<пароль>
DB_HOST=db  # в случаи езменения необходимо исправить файл docker-compose.yml 
DB_PORT=5432  # в случаи езменения необходимо исправить файл docker-compose.yml 
```
- Выполните команду для запуска контейнера:
```
sudo docker-compose up -d --build
``` 
- Выполнить миграции и подключить статику
```
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py collectstatic --noinput
``` 
- Создадим суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
``` 
### Проект
Работает по адресу http://158.160.4.219/
superuser : super@mail.ru
username: SuperUser
password: super342rf364g4645

### Документация
http://158.160.4.219/api/docs/


## Авторы проекта
### Скалацкий Владимир
e-mail: skalakcii@yandex.ru<br>
https://github.com/oitczvovi