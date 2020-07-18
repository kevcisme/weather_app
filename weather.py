from flask import Flask, render_template
from sense_hat import SenseHat

app = Flask(__name__)

@app.route('/')
def index():
    sense = SenseHat()
    celcius = round(sense.get_temperature(), 1)
    fahrenheit = round(1.8 * celcius + 32, 1)
