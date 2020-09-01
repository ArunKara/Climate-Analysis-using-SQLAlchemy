import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Setup Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurements = Base.classes.measurement
Stations = Base.classes.station
session = Session(engine)

#Setup Flask
app = Flask(__name__)

#List all routes
@app.route("/")

def homepage():
    return (
        f"Homepage of the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

#route for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precipitation = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date >= prev_year).all()

    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)





#route for stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Stations.station).all()

    stations = list(np.ravel(results))
    return jsonify(stations=stations)


#route for tobs
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurements.tobs).\
        filter(Measurements.station == 'USC00519281').\
        filter(Measurements.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


#route for start and end
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)]

    if not end:
        results = session.query(*sel). \
            filter(Measurements.date >= start).all()

        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurements.date >= start).\
        filter(Measurements.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)