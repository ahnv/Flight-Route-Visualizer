"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import jsonify
from FlightsFlask import app
from flask import request
from FlightsFlask.Flights import Flights

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/country')
def country():
    return render_template(
        'country.html',
        title='Country',
        year=datetime.now().year,
    )


@app.route('/api/country_check')
def country_check():
    flights = Flights()
    country = request.args.get("country")
    return jsonify(flights.check_if_country_exists(country))

@app.route('/api/country_process')
def country_process():
    flights = Flights()
    country = request.args.get("country")
    if country is not -1 or country is not 0:
        return jsonify({"simple" : flights.simple_visualization(country) , "advanced" : flights.advanced_visualization(country) , "stats" : flights.analysis(country)})
    return jsonify(flights.check_if_country_exists(country))