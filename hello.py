# необходимые импорты
import datetime
from flask import Flask, render_template, request, make_response, redirect, url_for
from db_util import Database

# инициализируем приложение
# из документации:
#     The flask object implements a WSGI application and acts as the central
#     object.  It is passed the name of the module or package of the
#     application.  Once it is created it will act as a central registry for
#     the view functions, the URL rules, template configuration and much more.
app = Flask(__name__)
app.secret_key = '11111'  # для безопасной работы сессии на стороне килента
app.permanent_session_lifetime = datetime.timedelta(days=365)  # сессия будет идти 365 дней

db = Database()
# дальше реализуем методы, которые мы можем выполнить из браузера,
# благодаря указанным относительным путям


# метод, который возвращает список фильмов по относительному адресу /films
@app.route("/films")
def films_list():
    country = request.args.get("country")  # достаем значение из гет-параметров(если не заданы - None)
    rating = request.args.get('rating') or 0
    rating = float(rating)

    # разные команды для получения фильмов из базы в зависимости от парметров запроса
    if rating and country:
        films = db.select(f"SELECT * FROM films WHERE UPPER(country) = UPPER('{country}') AND rating >= {rating};")
    elif country:
        films = db.select(f"SELECT * FROM films WHERE UPPER(country) = UPPER('{country}');")
    elif rating:
        films = db.select(f"SELECT * FROM films WHERE rating >= {rating};")
    else:
        films = db.select(f"SELECT * FROM films;")

    # формируем контекст, который мы будем передавать для генерации шаблона
    # получаем мод из cookies
    mode = request.cookies.get('mode') or 'light'
    context = {
        'films': films,
        'title': "FILMS",
        'country': country,
        'rating': rating,
        'style': mode
    }

    # возвращаем сгенерированный шаблон с нужным нам контекстом
    return render_template("films.html", **context)


# адрес, по которому можно отправлять и get, и post запросы
@app.route('/film_form', methods=['GET', 'POST'])
def render_form():
    mode = request.cookies.get('mode') or 'light'
    # если get запрос - просто рендерим страницу с формой
    if request.method == 'GET':
        return render_template('film_form.html', style=mode)

    # если post запрос - получаем данные из input
    name = request.form.get('name')
    rating = request.form.get('rating')
    country = request.form.get('country')

    # если одно из полей пустое - страницыа с ошибкой
    if not (name and rating and country):
        return render_template("error.html", error="Одно из полей пустое!", page='film_form', style=mode)

    # записываем полученные из формы данные
    db.insert(f"INSERT INTO films (name, rating, country) VALUES ('{name}', {float(rating)}, '{country}');")

    # формируем сообщение об успешном добавлении фильма
    response = f'Film "{name}" successfully added'
    context = {
        'response': response,
        'style': mode
    }

    # рендерим страничку с сообщением о добавлении фильма
    return render_template('film_form.html', **context)


# метод, который возвращает конкретный фильмо по id по относительному пути /film/<int:film_id>,
# где film_id - id необходимого фильма
@app.route("/film/<int:film_id>")
def get_film(film_id):
    # ищем нужный нам фильм и возвращаем шаблон с контекстом
    film = db.select(f'SELECT * FROM films WHERE id = {film_id}')

    mode = request.cookies.get('mode') or 'light'
    if len(film):
        return render_template('film.html', title=film[0]['name'], film=film[0], style=mode)

    # если нужный фильм не найден, возвращаем шаблон с ошибкой
    return render_template("error.html", error="Такого фильма не существует в системе", style=mode)


@app.route('/change_mode')
def change_mode():
    mode = request.cookies.get('mode') or 'light'
    # создаем новый cookie в заисимости какой стоит сейчас
    if mode == 'light':
        res = 'dark'
    else:
        res = 'light'

    # в ответ будем рендерить страницу, из которой перешли на /change_mode
    resp = make_response(redirect_back())
    resp.set_cookie('mode', res)

    return resp


def redirect_back(default='films', **kwargs):
    """Функция для перехода на предыдущую страницу"""
    # проверяем request.referrer - там лежит предыдущая страница(со всеми параметрами)
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        return redirect(target)
    return redirect(url_for(default, **kwargs))
