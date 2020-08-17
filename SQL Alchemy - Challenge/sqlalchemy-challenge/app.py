import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurements = Base.classes.measurement
Stations = Base.classes.station
session = Session(engine)
#FLASK SETUP
app = Flask(__name__)
def calc_temps(start, end):
        return session.query(func.min(Measurements.tobs),func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
            filter(Measurements.date >= start).filter(Measurements.date <= end).all()
print(calc_temps(start,end))

#list all the routes
@app.route("/")

def homepage():
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end>"
    )

#route for precipitation
@app.route("/api/v1.0/precipitation")

def precipitation():
    last_date = dt.date(2017, 8 ,23)
    previous_year = last_date - dt.timedelta(days=365)
    session = Session(engine)
    past_temp = (session.query(Measurements.date, Measurements.prcp)
                .filter(Measurements.date <= last_date)
                .filter(Measurements.date >= previous_year)
                .order_by(Measurements.date).all())
    
    precip = {date: prcp for date, prcp in past_temp}

    session.close()
    return jsonify(precip)

#route for stations
@app.route('/api/v1.0/stations')

def stations():
    session = Session(engine)

    stations_all = session.query(Stations.station).all()
    session.close()
    return jsonify(stations_all)

#route for tobs
@app.route('/api/v1.0/tobs') 
def tobs():  
    last_date = dt.date(2017, 8 ,23)
    previous_year = last_date - dt.timedelta(days=365)
    session = Session(engine)


    lastyear = (session.query(Measurements.tobs)
                .filter(Measurements.station == 'USC00519281')
                .filter(Measurements.date <= last_date)
                .filter(Measurements.date >= previous_year)
                .order_by(Measurements.tobs).all())
    session.close()
    return jsonify(lastyear)


#route for start

@app.route('/api/v1.0/<start>') 
def start():
    session = Session(engine)
    start = Measurements.date <= '2010-01-01'
    tobs_only = (session.query(Measurements.tobs).filter(Measurements.date.between(start, '2017-08-23')).all())
    tobs_df = pd.DataFrame(tobs_only)
    tobs_avg = tobs_df["tobs"].mean()
    tobs_max = tobs_df["tobs"].max()
    tobs_min = tobs_df["tobs"].min()
    session.close()
    return jsonify(tobs_avg, tobs_max, tobs_min)


#route for end
@app.route('/api/v1.0/<start>/<end>') 
def end():
    session = Session(engine)
    end = Measurements.date >= '2017-08-23'
    tobs_only = (session.query(Measurements.tobs).filter(Measurements.date.between(start, end)).all())
    tobs_df = pd.DataFrame(tobs_only)
    tobs_avg2 = tobs_df["tobs"].mean()
    tobs_max2 = tobs_df["tobs"].max()
    tobs_min2 = tobs_df["tobs"].min()
    session.close()
    return jsonify(tobs_avg2, tobs_max2, tobs_min2)

if __name__ == '__main__':
    app.run(debug=True)