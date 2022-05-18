import json
import sqlite3

from flask import Flask, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['DEBUG'] = True


def db_connect(query):
    connection = sqlite3.connect('netflix.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result


@app.route('/movie/<title>/')
def search_by_title(title):
    query = f"""
                SELECT title, country, release_year, listed_in AS genre, description
                FROM netflix
                WHERE title = '{title}'
                ORDER BY release_year DESC
                LIMIT 1
            """
    response = dict(db_connect(query)[0])

    return jsonify(response)


@app.route('/movie/<int:start>/to/<int:end>/')
def search_by_period_year(start, end):
    query = f"""
                SELECT title, release_year
                FROM netflix
                WHERE `release_year` BETWEEN {start} AND {end}
                ORDER BY release_year
                LIMIT 100
            """
    response = db_connect(query)

    response_json = []
    for film in response:
        response_json.append(dict(film))
    return jsonify(response_json)


@app.route('/rating/<group>/')
def search_by_rating(group):
    dict_ = {
        'children': ['G','G'],
        'family': ['G', 'PG', 'PG-13'],
        'adult': ['R', 'NC-17']
    }
    if not group in dict_:
        return jsonify(['Пусто'])

    query = f"""
                    SELECT title, rating, description
                    FROM netflix
                    WHERE rating IN {tuple(dict_[group])}
                    ORDER BY release_year
                    LIMIT 100
                """
    print(query)
    response = db_connect(query)
    # делаю словарь
    response_json = []
    for film in response:
        response_json.append({
            'title': film[0],
            'rating': film[1],
            'description': film[2].strip(),
        })
    return jsonify(response_json)


@app.route('/genre/<genre>/')
def search_by_genre(genre):
    query = f"""
                    SELECT title, description
                    FROM netflix
                    WHERE listed_in LIKE '%{genre}%'
                    ORDER BY release_year DESC
                    LIMIT 10
                """
    response = db_connect(query)

    response_json = []
    for film in response:
        response_json.append(
            dict(film)
        )
    return jsonify(response_json)


def get_actors(name_1, name_2):
    query = f"""
            SELECT "cast"
            FROM netflix
            WHERE "cast" LIKE '%{name_1}%'
            AND "cast" LIKE '%{name_2}%'
    """
    response = db_connect(query)
    actors = []
    for cast in response:
        actors.extend(cast[0].split(', '))
    result = []
    for i in actors:
        if i not in [name_1, name_2]:
            if actors.count(i) > 2:
                result.append(i)
    result = set(result)
    return result


def get_films(type_film, release_year, genre):
    query = f"""
            SELECT title, description, "type"
            FROM netflix
            WHERE "type" = '{type_film}'
            AND release_year = {release_year}
            AND listed_in LIKE '%{genre}%'
    """
    response = db_connect(query)
    response_json = []
    for film in response:
        response_json.append(dict(film))
    return json.dumps(response_json, ensure_ascii=False, indent=4)


print('GET FILMS', get_films(type_film='Movie', release_year=2016, genre='Dramas'))

print('GET ACTORS',get_actors(name_1='Rose McIver', name_2='Ben Lamb'))

if __name__ == '__main__':
    app.run()
