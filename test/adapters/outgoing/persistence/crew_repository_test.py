import pytest as pt
import os
import json
import arrow

import src.adapters.outgoing.persistence.crew_repository as repo

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
def skeleton_crew(db_path):
    return db_path + "/db_location/skeleton_crew.json"

@pt.fixture
def write_fail(db_path):
    file_path = db_path + "/db_location/write_fail.json"
    json.dump({}, open(file_path, "w"))
    return file_path

def test_does_not_load_data_store_file_successfully(nonexistent_db):
    test_repository = repo.CrewRepository(nonexistent_db)
    assert test_repository.db == {}

def test_raise_exception_if_invalid_json(invalid_crew):
    with pt.raises(json.decoder.JSONDecodeError):
        repo.CrewRepository(invalid_crew)

def test_loads_data_store_file_successfully(skeleton_crew):
    test_repository = repo.CrewRepository(skeleton_crew)
    assert test_repository.db != {}

def test_fail_to_write_data_store_file(write_fail):
    test_repository = repo.CrewRepository(write_fail)
    test_repository.db = float('nan')
    assert test_repository.writedb() == False

def test_write_data_store_file_successfully(skeleton_crew):
    test_repository = repo.CrewRepository(skeleton_crew)
    assert test_repository.writedb() == True

def test_does_not_find_pilots(skeleton_crew):
    repository = repo.CrewRepository(skeleton_crew)
    pilots = repository.get_pilots_for('Alabama', arrow.get('2020-05-01T09:00:00Z'), arrow.get('2020-05-03T11:00:00Z'))
    assert pilots == []

@pt.fixture
def find_daphne():
    return {
            'depart_on': '2020-05-01T09:00:00Z',
            'return_on': '2020-05-03T11:00:00Z',
            'base_location': 'Munich',
            'expected': [
                {
                    'ID': 4,
                    'Name': 'Daphne',
                    'Base': 'Munich',
                    'WorkDays': ['Friday', 'Saturday', 'Sunday']
                    }
                ]
            }

@pt.fixture
def find_multiple():
    return {
            'depart_on': '2020-05-02T09:00:00Z',
            'return_on': '2020-05-03T11:00:00Z',
            'base_location': 'Munich',
            'expected': [
                {
                    'ID': 3,
                    'Name': 'Callum',
                    'Base': 'Munich',
                    'WorkDays': ["Wednesday", "Thursday", "Saturday", "Sunday"]
                },
                {
                    'ID': 4,
                    'Name': 'Daphne',
                    'Base': 'Munich',
                    'WorkDays': ['Friday', 'Saturday', 'Sunday']
                }
            ]
    }

def test_get_single_pilot_for_location_and_dates(skeleton_crew, find_daphne):
    repository = repo.CrewRepository(skeleton_crew)
    pilots = repository.get_pilots_for(
            find_daphne['base_location'],
            find_daphne['depart_on'],
            find_daphne['return_on'])
    assert pilots == find_daphne['expected']

def test_get_multiple_pilot_for_location_and_dates(skeleton_crew, find_multiple):
    repository = repo.CrewRepository(skeleton_crew)
    pilots = repository.get_pilots_for(
            find_multiple['base_location'],
            find_multiple['depart_on'],
            find_multiple['return_on'])
    assert pilots == find_multiple['expected']
