import pytest as pt
import json
import arrow

import src.adapters.outgoing.persistence.crew_repository as repo
from fixtures.repository import db_path, nonexistent_db, invalid_crew, skeleton_crew, write_fail


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
    assert test_repository.writedb() is False


def test_write_data_store_file_successfully(skeleton_crew):
    test_repository = repo.CrewRepository(skeleton_crew)
    assert test_repository.writedb() is True
