import arrow
import json
import os
import pytest as pt

import src.adapters.outgoing.persistence.flights_repository as repo
from fixtures.repository import db_path, write_fail, nonexistent_db, invalid_flights, scheduled_flights

def test_does_not_load_data_store_file_successfully(nonexistent_db):
    test_repository = repo.FlightsRepository(nonexistent_db)
    assert test_repository.db == {}

def test_raise_exception_if_invalid_json(invalid_flights):
    with pt.raises(json.decoder.JSONDecodeError):
        repo.FlightsRepository(invalid_flights)

def test_loads_data_store_file_successfully(scheduled_flights):
    test_repository = repo.FlightsRepository(scheduled_flights)
    assert test_repository.db != {}

def test_fail_to_write_data_store_file(write_fail):
    test_repository = repo.FlightsRepository(write_fail)
    test_repository.db = float('nan')
    assert test_repository.writedb() == False

def test_write_data_store_file_successfully(scheduled_flights):
    test_repository = repo.FlightsRepository(scheduled_flights)
    assert test_repository.writedb() == True

def test_does_not_find_any_upcoming_flights_for_pilot(scheduled_flights):
    repository = repo.FlightsRepository(scheduled_flights)
    assert repository.get_upcoming_flights_for(pilots = [5]) == []

def test_finds_upcoming_flights_for_pilot(scheduled_flights):
    repository = repo.FlightsRepository(scheduled_flights)
    expected = [{
        "ID": 3,
        "Base": "Munich",
        "DepartureDateTime": "2022-06-01T09:00:00Z",
        "ReturnDateTime": "2022-06-03T11:00:00Z"
        }]
    assert repository.get_upcoming_flights_for(pilots = [3]) == expected

def test_schedule_flight_successfully(scheduled_flights):
    repository = repo.FlightsRepository(scheduled_flights)
    expected_flight = {
                "ID": 2,
                "Base": "Munich",
                "DepartureDateTime": "2021-12-01T09:00:00Z",
                "ReturnDateTime": "2021-12-03T11:00:00Z"
                }
    expected = {
            'status': 'Scheduled',
            'flight': {
                "ID": 2,
                "Base": "Munich",
                "DepartureDateTime": "2021-12-01T09:00:00Z",
                "ReturnDateTime": "2021-12-03T11:00:00Z"
                }
            }
    assert repository.schedule_flight_for(pilot=2, location='Munich', departure_dt= "2021-12-01T09:00:00Z", return_dt= "2021-12-03T11:00:00Z") == expected
    assert repository.get_upcoming_flights_for(pilots=[2]) == [expected_flight]

def test_handles_schedule_clashes_with_departure_time(scheduled_flights):
    repository = repo.FlightsRepository(scheduled_flights)
    expected = { 'status': 'ScheduleError: Clash' }
    assert repository.schedule_flight_for(pilot= 3, location='Munich', departure_dt= "2022-06-02T09:00:00Z", return_dt= "2022-06-05T11:00:00Z") == expected

def test_handles_schedule_clashes_with_return_time(scheduled_flights):
    repository = repo.FlightsRepository(scheduled_flights)
    expected = { 'status': 'ScheduleError: Clash' }
    assert repository.schedule_flight_for(pilot= 3, location='Munich', departure_dt= "2022-05-22T09:00:00Z", return_dt= "2022-06-02T11:00:00Z") == expected

def test_handles_schedule_clashes_with_depart_and_return_time(scheduled_flights):
    repository = repo.FlightsRepository(scheduled_flights)
    expected = { 'status': 'ScheduleError: Clash' }
    assert repository.schedule_flight_for(pilot= 3, location='Munich', departure_dt= "2022-06-01T09:00:00Z", return_dt= "2022-06-03T11:00:00Z") == expected

def test_does_not_schedule_departure_date_in_past(scheduled_flights):
    repository = repo.FlightsRepository(scheduled_flights)
    expected = { 'status': 'ScheduleError: InvalidDate' }
    assert repository.schedule_flight_for(pilot= 3, location='Munich', departure_dt= "2019-06-01T09:00:00Z", return_dt= "2022-05-03T11:00:00Z") == expected

def test_does_not_schedule_for_unordered_depart_and_return_date(scheduled_flights):
    repository = repo.FlightsRepository(scheduled_flights)
    expected = { 'status': 'ScheduleError: InvalidDate' }
    assert repository.schedule_flight_for(pilot= 3, location='Munich', departure_dt= "2021-06-01T09:00:00Z", return_dt= "2020-05-03T11:00:00Z") == expected

