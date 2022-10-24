# dependencies and setup
import datetime as dt
import numpy as np
import pandas as pd
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from sqlalchemy import and_, or_
from flask import Flask, app, jsonify

engine = create_engine(f'sqlite:///hawaii.sqlite')
insp = inspect(engine)
# check database table names
print(insp.get_table_names())
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# create our session (link) from Python to the DB
session = Session(engine)
# create Flask app
app = Flask(__name__)

# define welcome or index route
@app.route('/')
def welcome():
  return(
  f'Welcome to the Climate Analysis API!<br/>'
  f'Available Routes:<br/>'
  f'/api/v1.0/precipitation<br/>'
  f'/api/v1.0/stations<br/>'
  f'/api/v1.0/tobs<br/>'
  f'/api/v1.0/temp/start/end<br/>'
  )

# define the precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
  prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
  precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
  session.commit()
  precip = {date: prcp for date, prcp in precipitation}
  return jsonify(precip)

# define the stations route
@app.route('/api/v1.0/stations')
def stations():
  results = session.query(Station.station).all()
  session.commit()
  stations = list(np.ravel(results))
  return jsonify(stations=stations)

# define the temp route
@app.route('/api/v1.0/tobs')
def temp_monthly():
  prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
  results = session.query(Measurement.tobs).filter(and_(Measurement.station == 'USC00519281', Measurement.date >= prev_year)).all()
  session.commit()
  temps = list(np.ravel(results))
  return jsonify(temps=temps)

# define the stats route
@app.route('/api/v1.0/<start>/<end>')
def stats(start=None, end=None):
  sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
  if not end:
    results = session.query(*sel).filter(Measurement.date >= start).all()
    temps = list(np.ravel(results))
    return jsonify(temps)
  results = session.query(*sel).filter(and_(Measurement.date >= start, Measurement.date <= end)).all()
  session.commit()
  temps = list(np.ravel(results))
  return jsonify(temps=temps)

if __name__ == '__main__':
  app.run(debug=True)
