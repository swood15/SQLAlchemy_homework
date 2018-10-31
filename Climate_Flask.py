import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Define Flask routes
@app.route("/")
def welcome():
    return (
        f"AVAILABLE ROUTES:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/*start*<br/>"
        f"/api/v1.0/*start*/*end*"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    items = []
    results = session.query(Measurement.date, Measurement.prcp).all()
    for row in results:
        items.append({'date':row[0], 'prcp':row[1]})
    return jsonify(items)

@app.route("/api/v1.0/stations")
def stations():
    items = []
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    for row in results:
        items.append({'station':row[0], 'name':row[1], 'latitude':row[2], 'longitude':row[3], 'elevation':row[4]})
    return jsonify(items)

@app.route("/api/v1.0/tobs")
def tobs():
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(date[0], "%Y-%m-%d") - dt.timedelta(days=365)

    items = []
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > year_ago).all()

    for row in results:
        items.append({'date':row[0], 'tobs':row[1]})
    return jsonify(items)

@app.route("/api/v1.0/<start>")
def start():
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    print(start_date)
    
    items = []
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date > start_date).all()

    for row in results:
        items.append({'TMIN':row[0], 'TAVG':row[1], 'TMAX':row[2]})
    return jsonify(items)

if __name__ == "__main__":
    app.run(debug=True)