import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt  


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Use Flask to create your routes
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# List all routes that are available.
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href=/api/v1.0/precipitation> /api/v1.0/precipitation  </a><br/>"
        f"<a href=/api/v1.0/stations> /api/v1.0/stations  </a><br/>"
        f"<a href=/api/v1.0/tobs> /api/v1.0/tobs </a><br/>"
        f"/api/v1.0/&#60;start&#62;<br/>"
        f"/api/v1.0/&#60;start&#62;/&#60;end&#62;<br/>"
    )

 # Convert the query results to a dictionary using date as the key and prcp as the value.
 # Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)

    last_year = dt.date(2017,8,23) - dt.timedelta(days = 365)
    last_year

    # Query all 
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    session.close()

    prcp_dic = {date:prcp for date, prcp in results}
    
    return jsonify(prcp_dic)

#/api/v1.0/stations - Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query(Station.name).all()

    session.close()

    return jsonify(results)

#/api/v1.0/tobs
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    stmt = session.query(Measurement.station, func.count('*').label("station_count")).group_by(Measurement.station).subquery()

    topstation = ""
    topcount = 0
    for station, count in session.query(Measurement, stmt.c.station_count).outerjoin(stmt, Measurement.station == stmt.c.station).group_by(Measurement.station):
        if count > topcount:
            topstation = station
            topcount = count 
    print(topstation,topcount)
    results = session.query(Measurement.date,Measurement.station,Measurement.tobs).filter(Measurement.station == topstation.station).all()


    return jsonify(results) 
#/api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive


@app.route("/api/v1.0/<start>", defaults={'end': ""})
@app.route("/api/v1.0/<start>/<end>")
def start(start,end ):

    if end == "":
        end = dt.date.today()
        print("EndDate",end)
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<end).all()
    results_list = list(np.ravel(results))

    return jsonify(results_list)

    




if __name__ == '__main__':
    app.run(debug=True)
