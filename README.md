# hw05_final
## Описание
Блог, на котором пользователи могут регистрироваться, размещать свои записи, прикреплять картинки к записям. Пользователи могут подписываться друг на друга. Посты пользователей можно размещать в группы.  
**Стек технологий**
Python, Django, Django ORM.

## Запуск проекта
1. Клонировать репозиторий и перейти в него в командной строке  
git clone https://github.com/EvgeniyGartsev/hw05_final
cd hw05_final

2. Cоздать и активировать виртуальное окружение  
python3 -m venv venv
source venv/Scripts/activate

3. Обновить pip и установить зависимости из файла requirements.txt  
python -m pip install --upgrade pip
pip install -r requirements.txt

4. Перейти в директорию yatube и создать суперпользователя  
python manage.py createsuperuser

5. Выполнить миграции  
python manage.py migrate

6. Запустить проект  
python manage.py runserver
