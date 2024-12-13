# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
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
Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Home route that lists all available routes
@app.route('/')
def index():
    return (
        f"Welcome to the Climate API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end>"
    )

# Route 1: /api/v1.0/precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = (dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).date()

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()

    
    precipitation_data = {result[0]: result[1] for result in results}
    
    return jsonify(precipitation_data)

# Route 2: /api/v1.0/stations
@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station).all()

    stations_list = [result[0] for result in results]
    
    return jsonify(stations_list)

# Route 3: /api/v1.0/tobs
@app.route('/api/v1.0/tobs')
def tobs():
    
    most_active_station = 'USC00519281'
    recent_date = session.query(Measurement.date).filter(Measurement.station == most_active_station).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= year_ago
    ).all()

    tobs_list = [{"date": result[0], "temperature": result[1]} for result in results]

    return jsonify(tobs_list)

# /api/v1.0/<start>: Minimum, average, and maximum temperatures from a start date
@app.route("/api/v1.0/<start>")
def temp_start(start):
    results = session.query(
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()
    
    # Return the results as a dictionary
    temp_dict = {
        "Start Date": start,
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temp_dict)


# /api/v1.0/<start>/<end>: Minimum, average, and maximum temperatures between a start and end date
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    results = session.query(
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Return the results as a dictionary
    temp_dict = {
        "Start Date": start,
        "End Date": end,
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temp_dict)


if __name__ == "__main__":
    app.run(debug=True)