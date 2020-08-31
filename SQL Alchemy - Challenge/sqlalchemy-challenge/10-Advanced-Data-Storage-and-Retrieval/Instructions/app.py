#import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Setup Database
#create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#create base
Base = automap_base()
#connect base
Base.prepare(engine, reflect=True)
#measurements variable
Measurements = Base.classes.measurement
#stations variable
Stations = Base.classes.station
#create session
session = Session(engine)

#Setup Flask
app = Flask(__name__)

#list all the routes
@app.route("/")

#define homepage
def homepage():
    return (
        f"Homepage of the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

#create route for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precipitation = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date >= prev_year).all()

    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)





#create route for stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Stations.station).all()

    stations = list(np.ravel(results))
    return jsonify(stations=stations)


#create route for tobs
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurements.tobs).\
        filter(Measurements.station == 'USC00519281').\
        filter(Measurements.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


#create route for start date and end date
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
