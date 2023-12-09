# Import the dependencies.
import numpy as np
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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
#Homepage route
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
# Calculate the date one year ago from the recent date
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#Convert the query results from precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    date_prcp_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    prcp_dict = {date: prcp for date, prcp in date_prcp_query}
    return jsonify(prcp_dict)

#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.station).all()
    all_stations = list(np.ravel(stations_query))
    return jsonify(all_stations)

#Return a JSON list of temperature observations of the most-active station for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_query = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.station == 'USC00519281').all()
    all_tobs_measurements = []
    for date, tobs in tobs_query:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs_measurements.append(tobs_dict)
    return jsonify(all_tobs_measurements)

#Return a JSON list of the min, avg, and max temperature for a specified start
@app.route("/api/v1.0/<start>")
def start(start):
    starting_day = datetime.strptime(start, '%Y-%m-%d')
    start_date_tobs = session.query(Measurement.tobs).\
        filter(Measurement.date >= starting_day).all()
    t_list = list(np.ravel(start_date_tobs))
    t_min = min(t_list)
    t_avg = np.mean(t_list)
    t_max = max(t_list)
    temperature_values = [{"minimum temperature":t_min}, {"average temperature":t_avg}, {"maximum temperature":t_max}]
    return jsonify(temperature_values)
    
#Return a JSON list of the min, avg, and max temperature for a specified start-end range
@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    starting_day = datetime.strptime(start, '%Y-%m-%d')
    ending_day = datetime.strptime(end, '%Y-%m-%d')
    start_end_date_tobs = session.query(Measurement.tobs).\
          filter(Measurement.date >= starting_day, Measurement.date <= ending_day).all()
    t_list = list(np.ravel(start_end_date_tobs))
    t_min = min(t_list)
    t_avg = np.mean(t_list)
    t_max = max(t_list)
    temperature_values = [{"minimum temperature":t_min}, {"average temperature":t_avg}, {"maximum temperature":t_max}]
    return jsonify(temperature_values)

if __name__ == '__main__':
    app.run(debug=True)