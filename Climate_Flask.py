import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Find latest record in dataset
last = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
first = session.query(Measurement.date).order_by(Measurement.date.asc()).first()

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
        f"/api/v1.0/start*<br/>"
        f"/api/v1.0/start*/end*<br/>"
        f"* start/end dates should use the format yyyy-mm-dd (e.g., 2017-01-01)."
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
    year_ago = dt.datetime.strptime(last[0], "%Y-%m-%d") - dt.timedelta(days=365)

    items = []
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > year_ago).all()

    for row in results:
        items.append({'date':row[0], 'tobs':row[1]})
    return jsonify(items)

@app.route("/api/v1.0/<start>")
def start_search(start):
    if start > last[0]:
        return jsonify({"ERROR": f"Invalid start date, cannot be after {last[0]}."}), 404
    elif start < first[0]:
        return jsonify({"ERROR": f"Invalid start date, cannot be before {first[0]}."}), 404
    else:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date > (start_date  - dt.timedelta(days=1))).all()
        return jsonify({'TMIN':results[0][0], 'TAVG':results[0][1], 'TMAX':results[0][2]})

@app.route("/api/v1.0/<start>/<end>")
def start_end_search(start, end):
    if start > last[0] or end > last[0]:
        return jsonify({"ERROR": f"Invalid date, cannot be after {last[0]}."}), 404
    elif start < first[0] or end < first[0]:
        return jsonify({"ERROR": f"Invalid date, cannot be before {first[0]}."}), 404
    elif start > end:
        return jsonify({"ERROR": f"Start date cannot be after end date."}), 404
    else:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date > (start_date - dt.timedelta(days=1))).\
            filter(Measurement.date < (end_date + dt.timedelta(days=1))).all()
        return jsonify({'TMIN':results[0][0], 'TAVG':results[0][1], 'TMAX':results[0][2]})

if __name__ == "__main__":
    app.run(debug=True)