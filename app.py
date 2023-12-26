# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session()
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= one_year_ago) \
        .order_by(Measurement.date).all()

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    session.close()
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session()
    stations = session.query(Station.station, Station.name).all()

    stations_list = [{"Station": station, "Name": name} for station, name in stations]
    session.close()
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session()

    most_active_station = session.query(Measurement.station, func.count(Measurement.station)) \
        .group_by(Measurement.station) \
        .order_by(func.count(Measurement.station).desc()).first()[0]
    
    latest_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)

    temperature_data = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.station == most_active_station) \
        .filter(Measurement.date >= one_year_ago).all()

    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]
    session.close()

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    session = Session()

    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

    temperature_stats = session.query(func.min(Measurement.tobs).label("TMIN"),
                                      func.avg(Measurement.tobs).label("TAVG"),
                                      func.max(Measurement.tobs).label("TMAX")) \
        .filter(Measurement.date >= start_date).all()

    tmin, tavg, tmax = temperature_stats[0]

    temp_stats_dict = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }
    session.close()

    return jsonify(temp_stats_dict)


@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    session = Session()

    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    temperature_stats = session.query(func.min(Measurement.tobs).label("TMIN"),
                                      func.avg(Measurement.tobs).label("TAVG"),
                                      func.max(Measurement.tobs).label("TMAX")) \
        .filter(Measurement.date >= start_date) \
        .filter(Measurement.date <= end_date).all()

    tmin, tavg, tmax = temperature_stats[0]

    temp_stats_dict = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }
    session.close()

    return jsonify(temp_stats_dict)


if __name__ == '__main__':
    app.run(debug=False)
        