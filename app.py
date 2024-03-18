from flask import Flask, request, render_template, jsonify
from Service.service import get_autocomplete_suggestion, get_recommended_movies
import json
from flask_socketio import SocketIO

app = Flask('Movie Recommendation Engine')
socketio = SocketIO(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/get-movies-list', methods=['POST'])
def get_movies_list_suggestions():
    movie_lists = get_autocomplete_suggestion(request.data.decode("utf-8").lower()[1:-1])
    return jsonify(movie_lists)


@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    recommendations = get_recommended_movies(request.data.decode("utf-8")[1:-1])
    return json.dumps(recommendations)


if __name__ == '__main__':
    socketio.run(app)

