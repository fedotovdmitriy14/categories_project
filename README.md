# categories_project

**Запуск:**

В корне проекта создать файл с переменными окружения на основе .env.example

docker-compose up --build -d

Выполнить скрипт из dump.sql

Заполнить редис данными из бд:
curl -X 'POST' \
  'http://0.0.0.0:8080/api/v1/categories/redis' \
  -H 'accept: application/json' \
  -d ''

В финальной версии будет скрипт, обновляющий редис при запуске приложения

**Адреса фронтенда:**

http://0.0.0.0:8080/tree - главная страница
http://0.0.0.0:8080/single_category/id - страница категории
