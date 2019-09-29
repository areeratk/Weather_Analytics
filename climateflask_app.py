import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta
from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# connect to sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
#Home page.
def welcome():
   """List all available api routes."""
   return (
       f"Welcome to Climate App API<br/>"
       f"------------------------------------<br><br/>"
       f"Available API Routes:<br/><br/>"
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/yyyy-mm-dd<br/>"
       f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
   )

@app.route("/api/v1.0/precipitation")
def precipitation():
   """Convert the query results to a Dictionary using date as the key and prcp as the value."""
   # Find the last date of the dataset and calculate the date 1 year ago from the last data point in the database
   last_date = session.query(Measurement).order_by(Measurement.date.desc()).first().date
   first_date = (pd.to_datetime(last_date) - timedelta(days=365)).date()
   # Query to retrieve the last 12 months of precipitation data
   results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > first_date).all()
   """Return the JSON representation of your dictionary."""
   precipitation_dict= {}
   for date, prcp in results:
       precipitation_dict[date] = prcp
   return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
   """Return a JSON list of stations from the dataset."""
   # Query all stations
   all_stations = session.query(Station).order_by(Station.id.asc()).all()
   list_stations = []
   for value in all_stations:
       station_dict = {}
       station_dict["station"] = value.station
       station_dict["name"] = value.name
       station_dict["latitude"] = value.latitude
       station_dict["longitude"] = value.longitude
       station_dict["elevation"] = value.elevation
       station_dict["_id"] = value.id
       list_stations.append(station_dict)
   return jsonify(list_stations)

@app.route("/api/v1.0/tobs")
def tobs():
   """Query for the dates and temperature observations from a year from the last data point."""
   # Find the last date of the dataset and calculate the date 1 year ago from the last data point in the database
   last_date = session.query(Measurement).order_by(Measurement.date.desc()).first().date
   first_date = (pd.to_datetime(last_date) - timedelta(days=365)).date()
   # Query to retrieve the last 12 months of temperatures
   results_s = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > first_date)
   """Return a JSON list of Temperature Observations (tobs) for the previous year."""
   dict_temp = {}
   for date, tobs in results_s:
       dict_temp[date] = tobs
   temp_list = list(np.ravel(dict_temp))
   return jsonify(temp_list)   

@app.route("/api/v1.0/<start>")
def start(start):
   # Format date
   start_date = pd.to_datetime(start).strftime("%Y-%m-%d")
   """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start"""
   # Select the values to query
   sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
   # Query the data
   start_tobs = session.query(*sel).filter(Measurement.date >= start_date).all()
   """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date"""
   tobs = []
   for tmin, tavg, tmax in start_tobs:
       temp_dict= {}
       temp_dict["TMIN"] = tmin
       temp_dict["TAVG"] = tavg
       temp_dict["TMAX"] = tmax
       tobs.append(temp_dict)
   tobslist = list(np.ravel(tobs))
   return jsonify(tobslist)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
   # Format dates
   start_date = pd.to_datetime(start).strftime('%Y-%m-%d')
   end_date = pd.to_datetime(end).strftime('%Y-%m-%d')
   """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a date range"""
   # Select the values to query
   sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
   # Query the data
   start_end_tobs = session.query(*sel).filter(Measurement.date > start_date).filter(Measurement.date < end_date)
   tobs = []
   for tmin, tavg, tmax in start_end_tobs:
       temp_dict= {}
       temp_dict["TMIN"] = tmin
       temp_dict["TAVG"] = tavg
       temp_dict["TMAX"] = tmax
       tobs.append(temp_dict)
   tobslist = list(np.ravel(tobs))
   return jsonify(tobslist)

@app.route("/api/v1.0/yyyy-mm-dd")
#Output from the @app.route("/api/v1.0/<start>")
def output_start():
   return (f"Input a start date in place of yyyy-mm-dd on the URL to calculate TMIN, TAVG, and TMAX ... "
   f"for dates greater than or equal to the start date.")

@app.route("/api/v1.0/yyyy-mm-dd/yyyy-mm-dd")
#Output from the @app.route("/api/v1.0/<start>/<end>")
def output_start_end():
   return (f"Input a start date/an end date in place of yyyy-mm-dd/yyyy-mm-dd on the URL to calculate TMIN, TAVG, and TMAX ... "
   f"for dates between the start and end dates.")

if __name__ == "__main__":
   app.run(debug=True)