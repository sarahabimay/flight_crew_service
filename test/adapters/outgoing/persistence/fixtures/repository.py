import pytest as pt
import os
import json


@pt.fixture
def db_path():
    return os.path.dirname(os.path.abspath(__file__))


@pt.fixture
def nonexistent_db(db_path):
    return db_path + "/db_location/nonexistent.json"


@pt.fixture
def invalid_crew(db_path):
    return db_path + "/db_location/invalid_crew.json"


@pt.fixture
def invalid_flights(db_path):
    return db_path + "/db_location/invalid_flights.json"


@pt.fixture
def skeleton_crew(db_path):
    return db_path + "/db_location/skeleton_crew.json"


@pt.fixture
def scheduled_flights(db_path):
    reset_file = db_path + "/reset/scheduled_flights.json"
    scheduled_flights_db = db_path + "/db_location/scheduled_flights.json"
    json.dump(json.load(open(reset_file, "r")), open(scheduled_flights_db, "w"))
    return scheduled_flights_db


@pt.fixture
def flights_history(db_path):
    return db_path + "/db_location/flights_history.json"


@pt.fixture
def write_fail(db_path):
    file_path = db_path + "/db_location/write_fail.json"
    json.dump({}, open(file_path, "w"))
    return file_path
