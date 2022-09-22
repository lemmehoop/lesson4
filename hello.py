import json

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/films")
def films_list():
    with open("films.json", 'r') as f:
        films = json.load(f)

    country = request.args.get("country")

    context = {
        'films': films,
        'title': "FILMS",
        'country': country
    }

    return render_template("films.html", **context)


@app.route("/film/<int:film_id>")
def get_film(film_id):
    with open("films.json", 'r') as f:
        films = json.load(f)

    for film in films:
        if film['id'] == film_id:
            return render_template("film.html", title=film['name'], film=film)

    return render_template("error.html", error="Такого фильма не существует в системе")
