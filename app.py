from flask import Flask
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

@app.route('/')
def greet_user():
    # Set the timezone to New York
    new_york_timezone = timezone('America/New_York')
    current_time = datetime.now(new_york_timezone)
    current_hour = current_time.hour

    # Greet the user based on the current hour
    if 5 <= current_hour < 12:
        greeting = 'Good morning!'
    elif 12 <= current_hour < 17:
        greeting = 'Good afternoon!'
    elif 17 <= current_hour < 21:
        greeting = 'Good evening!'
    else:
        greeting = 'Good night!'

    return f'{greeting} Welcome to the Flask app!'

if __name__ == '__main__':
    app.run(debug=True)
