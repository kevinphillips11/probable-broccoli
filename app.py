from flask import Flask, render_template, request, Blueprint
import csv
import random

app = Flask(__name__)

# Blueprint for movies
movies_blueprint = Blueprint('movies', __name__, template_folder='templates')

# Blueprint for stars
stars_blueprint = Blueprint('stars', __name__, template_folder='templates')

random_movie_blueprint = Blueprint('random', __name__, template_folder='templates')

# Configurations
PAGE_SIZE = 9


@movies_blueprint.route('/')
def movies():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', None)
    sort_order = request.args.get('sort', 'asc')

    movies_list = []
    with open('./data/movies.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if search_query is None or search_query.lower() in row['Title'].lower():
                movies_list.append(row)

    # Sort by duration if requested
    if sort_order == 'desc':
        movies_list.sort(key=lambda x: int(x['Duration']), reverse=True)
    else:
        movies_list.sort(key=lambda x: int(x['Duration']))

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE

    # Load movie images
    movie_images = {}
    with open('./data/images.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Title'] in movie_images:
                continue
            movie_images[row['Title']] = row['URL']

    # Add image URL to each movie
    for movie in movies_list:
        movie['Image'] = movie_images.get(movie['Title'], None)

    return render_template('movies.html', movies=movies_list[start:end], page=page, search_query=search_query, sort_order=sort_order)


@movies_blueprint.route('/<title>')
def movie(title):
    with open('./data/movies.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Title'] == title:
                movie_data = row
                break

    images_list = []
    with open('./data/images.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Title'] == title:
                images_list.append(row['URL'])

    stars_list = []
    with open('./data/movie_stars.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Title'] == title:
                stars_list.append(row['Name'])

    return render_template('movie.html', movie=movie_data, images=images_list, stars=stars_list)


@stars_blueprint.route('/')
def stars():
    page = request.args.get('page', 1, type=int)
    letter = request.args.get('letter', 'All Stars')
    
    stars_list = []
    with open('./data/stars.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if letter == 'All Stars' or row['Name'].startswith(letter):
                stars_list.append(row)

    # Sort stars alphabetically
    stars_list.sort(key=lambda x: x['Name'])

    # Load star images
    star_images = {}
    with open('./data/model-images.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            star_images.setdefault(row['Model Name'], []).append(row['Image_URL'])

    for star in stars_list:
        star['Images'] = star_images.get(star['Name'], [])

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE

    return render_template('stars.html', stars=stars_list[start:end], page=page, letter=letter)



@stars_blueprint.route('/<name>')
def star(name):
    # Load star details
    star_data = None
    with open('./data/stars.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name'] == name:
                star_data = row
                break

    if not star_data:
        # You can redirect to a 404 page or another appropriate action if star not found
        return "Star not found!", 404

    # Load star's movies
    movies_list = []
    with open('./data/movie_stars.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name'] == name:
                movies_list.append(row['Title'])

    # Load star's images
    star_images = []
    with open('./data/model-images.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Model Name'] == name:
                star_images.append(row['Image_URL'])

    star_data['Images'] = star_images

    return render_template('star.html', star=star_data, movies=movies_list)


@app.route('/random')
def random_movie():
    # Load star's movies
    movies = {}
    with open('./data/movie_stars.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # movies_list.append(row['Title'])
            movies[row['Title']] = []

    movies = {key: movies[key] for key in random.sample(movies.keys(), 5)}

    images_list = []
    with open('./data/images.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Title'] in movies.keys():
                #images_list.append(row['URL'])
                movies[row['Title']].append(row['URL'])

    

    return render_template('random.html',movies=movies)


@app.route('/')
def index():
    return render_template('index.html')


# Register the blueprints
app.register_blueprint(movies_blueprint, url_prefix='/movies')
app.register_blueprint(stars_blueprint, url_prefix='/stars')


def start_app():
    app.run(debug=True)
