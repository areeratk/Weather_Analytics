import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta
from flask import Flask, jsonify
#################################################
# Reflect Tables
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################

app = Flask(__name__)
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
   """List all available api routes."""
   # Create our session (link) from Python to the DB
   session = Session(engine)
   last_data = session.query(Measurement).order_by(Measurement.date.desc()).first().date
   first_data = session.query(Measurement).order_by(Measurement.date.asc()).first().date
   session.close()
   return (
       f"--------------- Welcome to Surf Up API ------------------<br/>"
       f"----------------------------------------------------------------<br/>"
       f'Dataset available from: {first_data} to: {last_data}<br/>'
       f"----------------------------------------------------------------<br/>"
       f"Available Routes:<br/><br/>"
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/yyyymmdd<br/>"
       f"/api/v1.0/yyyymmdd/yyyymmdd/"
   )
@app.route("/api/v1.0/precipitation")
def precipitation():
   # Create our session (link) from Python to the DB
   session = Session(engine)
   """Convert the query results to a Dictionary using date as the key and prcp as the value."""
   # Find the last date of the dataset and calculate the date one year before
   last_date = session.query(Measurement).order_by(Measurement.date.desc()).first().date
   first_date = (pd.to_datetime(last_date) - timedelta(days=365)).date()
   # Query precipitations for the last year of the dataset
   results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).all()
   session.close()
   # Create a dictionary
   precipitation_dict= {}
   for date, prcp in results:
       precipitation_dict[date] = prcp
   return jsonify(precipitation_dict)
@app.route("/api/v1.0/stations")
def stations():
   session = Session(engine)
   """Return a JSON list of stations from the dataset."""
   # Query all stations
   all_stations = session.query(Station).order_by(Station.id.asc()).all()
   session.close()
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
   #list_stations = list(np.ravel(stations_list))
   return jsonify(list_stations)
@app.route("/api/v1.0/tobs")
def tobs():
   # Create our session (link) from Python to the DB
   session = Session(engine)
   """Query for the dates and temperature observations from a year from the last data point."""
   # Calculate the date 1 year ago from the last data point in the database
   last_date = session.query(Measurement).order_by(Measurement.date.desc()).first().date
   first_date = (pd.to_datetime(last_date) - timedelta(days=365)).date()
   # Perform a query to retrieve the data and temperatures for this period
   datas = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= first_date)
   session.close()
   dict_temp = {}
   for date, tobs in datas:
       dict_temp[date] = tobs
   temp_list = list(np.ravel(dict_temp))
   return jsonify(temp_list)
@app.route("/api/v1.0/<start>")
def start(start):
   # Convert the string in the good format
   start_date = pd.to_datetime(start).strftime("%Y-%m-%d")
   # Create our session (link) from Python to the DB
   session = Session(engine)
   """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start"""
   # Select the values for the query
   sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs),
  func.max(Measurement.tobs)]
   # Perform a query to retrieve the data and temperatures for this period
   start_temperatures = session.query(*sel).filter(Measurement.date >= start_date).all()
   session.close()
   tobs = []
   for tmin, tavg, tmax in start_temperatures:
       temp_dict= {}
       temp_dict["TMIN"] = tmin
       temp_dict["TAVG"] = tavg
       temp_dict["TMAX"] = tmax
       tobs.append(temp_dict)
   tobslist = list(np.ravel(tobs))
   return jsonify(tobslist)
@app.route("/api/v1.0/<start>/<end>/")
def start_end(start, end):
   # Convert the string in the good format
   start_date = pd.to_datetime(start).strftime("%Y-%m-%d")
   end_date = pd.to_datetime(end).strftime("%Y-%m-%d")
   # Create our session (link) from Python to the DB
   session = Session(engine)
   """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a start-end"""
   # Select the values for the query
   sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs),
  func.max(Measurement.tobs)]
   # Perform a query to retrieve the data and temperatures for this period
   start_end_temperatures = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
   session.close()
   tobs = []
   for tmin, tavg, tmax in start_end_temperatures:
       temp_dict= {}
       temp_dict["TMIN"] = tmin
       temp_dict["TAVG"] = tavg
       temp_dict["TMAX"] = tmax
       tobs.append(temp_dict)
   tobslist = list(np.ravel(tobs))
   return jsonify(tobslist)
@app.route("/api/v1.0/yyyymmdd")
def reroute():
   return (f"Input a start date in the format yyyymmdd to calculate TMIN, TAVG, and TMAX"
   f"for all dates greater than and equal to the start date.")
@app.route("/api/v1.0/yyyymmdd/yyyymmdd/")
def reroute2():
   return (f"Input a start date and a end date in the format yyyymmdd to calculate TMIN, TAVG, and TMAX"
   f"for dates between the start and end date inclusive.")
if __name__ == "__main__":
   app.run(debug=True)