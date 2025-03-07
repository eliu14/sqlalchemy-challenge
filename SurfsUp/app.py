# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date_point = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    one_year_date = recent_date_point - dt.timedelta(days=366)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_date).\
        filter(Measurement.prcp >= 0).all()
    prcp_dict = {}
    for data in results:
        prcp_dict[data.date] = data.prcp
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station,Station.name).all()
    dict = {}
    for station in stations:
        dict[station.station] = station.name
    return jsonify(dict)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_stations = session.query(Measurement.station, func.count(Measurement.prcp)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.prcp).desc()).all()
    most_active_station = most_active_stations[0].station
    
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date_point = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    one_year_date = recent_date_point - dt.timedelta(days=366)
    
    result = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_date).\
        filter(Measurement.station == most_active_station).all()
    dict = {}
    for data in result:
        dict[data.date] = data.tobs
    return jsonify(dict)

@app.route("/api/v1.0/<start>")
def tobs_start_date(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    result_dict = {
        "TMIN": result[0][0],
        "TAVG": result[0][2],
        "TMAX": result[0][1]
    }
    return jsonify(result_dict)
@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end_date(start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    result_dict = {
        "TMIN": result[0][0],
        "TAVG": result[0][2],
        "TMAX": result[0][1]
    }
    return jsonify(result_dict)
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Returns dictionary representation of query results from my precipitation analysis<br/>"
        f"/api/v1.0/stations - Returns JSON list of stations<br/>"
        f"/api/v1.0/tobs - Return a JSON list of temperature observations for the previous year.<br/>"
        f"/api/v1.0/<start> - Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start<br/>"
        f"/api/v1.0/<start>/<end> - Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range<br/>"
    )
if __name__ == "__main__":
    app.run(debug=True)