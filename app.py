from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pickle
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def recommend(anime):
    index = animes[animes['title'] == anime].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_animes = []
    for i in distances[1:10]:
        recommended_anime = {
            'title': animes.iloc[i[0]].title,
            'image_url': animes.iloc[i[0]].img_url,
            'link': animes.iloc[i[0]].link
        }
        recommended_animes.append(recommended_anime)

    return recommended_animes
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def home():
    message = None

    if request.method == 'POST':
        if 'signup' in request.form:
            username = request.form['username']
            password = request.form['password']

            # Check if username already exists
            with app.app_context():
                existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                message = 'Username already exists. Please choose another.'
            else:
                # Store user information in the database
                with app.app_context():
                    new_user = User(username=username, password=password)
                    db.session.add(new_user)
                    db.session.commit()
                message = 'Signup successful!'

        elif 'login' in request.form:
            username = request.form['username']
            password = request.form['password']

            # Retrieve user information from the database
            with app.app_context():
                user = User.query.filter_by(username=username, password=password).first()

            if user:
                message = f'Welcome, {username}! You have successfully logged in.'
                # Redirect to the homepage after successful login
                return redirect(url_for('homepage'))
            else:
                message = 'Invalid username or password. Please try again.'

    return render_template('home.html', message=message)

@app.route('/homepage')
def homepage():
    return render_template('homepage.html',anime_list=animes["title"].values)

@app.route('/recommend', methods=['GET', 'POST'])
def recommendation():
    if request.method == 'POST':
        selected_anime = request.form['selected_anime']
        recommended_animes = recommend(selected_anime)

        return render_template('homepage.html', recommended_animes=recommended_animes)

if __name__ == '__main__':
    animes = pickle.load(open('models/animes.pkl', 'rb'))
    similarity = pickle.load(open('models/similarity.pkl', 'rb'))
    with app.app_context():
        db.create_all()
    app.run(debug=True)
