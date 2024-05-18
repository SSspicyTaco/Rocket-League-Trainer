pip install flask

from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

# Global variables
points = 0
casual_games_played = 0
daily_casual_games_limit = 5

# Load game state from file (if exists)
def load_game_state():
    global points
    global casual_games_played
    try:
        with open("game_state.json", "r") as f:
            game_state = json.load(f)
            points = game_state["points"]
            casual_games_played = game_state["casual_games_played"]
    except FileNotFoundError:
        print("No previous game state found.")

# Save game state to a JSON file
def save_game_state():
    game_state = {
        "points": points,
        "casual_games_played": casual_games_played
    }
    with open("game_state.json", "w") as f:
        json.dump(game_state, f)

# Function to calculate points earned based on time played
def calculate_points(time_played):
    minutes_played = time_played * 60
    points_per_interval = 1000
    interval_duration = 33  # minutes
    
    # Calculate number of intervals played
    intervals_played = minutes_played // interval_duration
    
    # Calculate total points earned
    total_points = intervals_played * points_per_interval
    
    return total_points

@app.route('/')
def index():
    load_game_state()
    return render_template('index.html', points=points, casual_games_played=casual_games_played)

@app.route('/play_casual_game', methods=['POST'])
def play_casual_game():
    global points, casual_games_played
    if casual_games_played < daily_casual_games_limit:
        score = int(request.form['score'])
        won_game = request.form['won_game'].lower()
        if won_game == "yes":
            points += 250
        points += score / 2
        casual_games_played += 1
        save_game_state()
        return jsonify(success=True, points=points, casual_games_played=casual_games_played)
    return jsonify(success=False, message="Daily limit reached")

@app.route('/play_competitive_game', methods=['POST'])
def play_competitive_game():
    global points
    score = int(request.form['score'])
    won_game = request.form['won_game'].lower()
    if won_game == "yes":
        points += 250
    points += score / 2
    save_game_state()
    return jsonify(success=True, points=points)

@app.route('/buy_power_up', methods=['POST'])
def buy_power_up():
    global points
    power_up = request.form['power_up']
    if power_up == "coaching_session" and points >= 5000:
        points -= 5000
    elif power_up == "new_workshop_map" and points >= 5000:
        points -= 5000
    elif power_up == "que_with_pro" and points >= 7500:
        points -= 7500
    else:
        return jsonify(success=False, message="Not enough points or invalid power-up")
    save_game_state()
    return jsonify(success=True, points=points)

@app.route('/add_time_played', methods=['POST'])
def add_time_played():
    global points
    time_played = float(request.form['time_played'])
    points += calculate_points(time_played)
    save_game_state()
    return jsonify(success=True, points=points)

if __name__ == "__main__":
    app.run(debug=True)
