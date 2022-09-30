# необходимые импорты
import json
from flask import Flask, render_template, request

# инициализируем приложение
# из документации:
#     The flask object implements a WSGI application and acts as the central
#     object.  It is passed the name of the module or package of the
#     application.  Once it is created it will act as a central registry for
#     the view functions, the URL rules, template configuration and much more.
app = Flask(__name__)

# дальше реализуем методы, которые мы можем выполнить из браузера,
# благодаря указанным относительным путям


# метод, который возвращает список фильмов по относительному адресу /films
@app.route("/films")
def films_list():
    # читаем файл с фильмами
    with open("films.json", 'r') as f:
        films = json.load(f)

    # получаем GET-параметр country (Russia/USA/French)
    country = request.args.get("country")
    rating = request.args.get('rating')
    # фильтрация фильмов по рейтингу, полученному из get запроса
    if rating:
        films = list(filter(lambda x: x['rating'] >= float(rating), films))

    # формируем контекст, который мы будем передавать для генерации шаблона
    context = {
        'films': films,
        'title': "FILMS",
        'country': country,
        'rating': rating
    }

    # возвращаем сгенерированный шаблон с нужным нам контекстом
    return render_template("films.html", **context)


# адрес, по которому можно отправлять и get, и post запросы
@app.route('/film_form', methods=['GET', 'POST'])
def render_form():
    # если get запрос - просто рендерим страницу с формой
    if request.method == 'GET':
        return render_template('film_form.html')

    # если post запрос - получаем данные из инпутов
    name = request.form.get('name')
    rating = request.form.get('rating')
    country = request.form.get('country')

    # получаем данные из json
    with open('films.json') as f:
        films = json.load(f)

    # если одно из полей пустое - страницыа с ошибкой
    if not (name and rating and country):
        return render_template("error.html", error="Одно из полей пустое!", page='film_form')

    # словарь с новым фильмом
    new = {
        'id': films[-1]['id'] + 1,
        'name': name,
        'rating': float(rating),
        'country': country
    }

    # добавляем филм в общий словарь
    films.append(new)
    with open('films.json', 'w') as f:
        # записываем словарь в файл
        json.dump(films, f, indent=2)

    # формируем сообщение об успешном добавлении фильма
    response = f'Film "{name}" successfully added'
    context = {
        'response': response,
    }

    # рендерим страничку с сообщением о добавлении фильма
    return render_template('film_form.html', **context)


# метод, который возвращает конкретный фильмо по id по относительному пути /film/<int:film_id>,
# где film_id - id необходимого фильма
@app.route("/film/<int:film_id>")
def get_film(film_id):
    # читаем файл
    with open("films.json", 'r') as f:
        films = json.load(f)

    # ищем нужный нам фильм и возвращаем шаблон с контекстом
    for film in films:
        if film['id'] == film_id:
            return render_template("film.html", title=film['name'], film=film)

    # если нужный фильм не найден, возвращаем шаблон с ошибкой
    return render_template("error.html", error="Такого фильма не существует в системе")
