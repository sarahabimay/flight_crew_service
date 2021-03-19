import json
import pytest as pt

import src.adapters.outgoing.persistence.flights_repository as repo
from fixtures.repository import db_path, nonexistent_db, invalid_flights, scheduled_flights, write_fail


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


