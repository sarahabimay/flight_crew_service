import json
import os

import pytest as pt

from src.adapters.outgoing.persistence.crew_repository import CrewRepository
from src.adapters.outgoing.persistence.entity_factory import EntityFactory
from src.adapters.outgoing.persistence.flights_repository import FlightsRepository

from fixtures.repository import invalid_crew, db_path


@pt.fixture
def repo_path():
    return os.path.dirname(os.path.abspath(__file__))


@pt.fixture
def reset_crew_repository(repo_path):
    reset_file = repo_path + "/fixtures/reset/crew.json"
    crew_repo_location = repo_path + "/fixtures/db_location/crew.json"
    json.dump(json.load(open(reset_file, "r")), open(crew_repo_location, "w"))
    return crew_repo_location


@pt.fixture
def reset_scheduled_flights(repo_path):
    reset_file = repo_path + "/fixtures/reset/scheduled_flights.json"
    scheduled_flights_db = repo_path + "/fixtures/db_location/scheduled_flights.json"
    json.dump(json.load(open(reset_file, "r")), open(scheduled_flights_db, "w"))
    return scheduled_flights_db


def test_cannot_create_unknown_repository(reset_crew_repository):
    entity_factory = EntityFactory()
    repository = entity_factory.entity('unknown', reset_crew_repository)
    assert repository is None


def test_cannot_create_unknown_repository(reset_crew_repository):
    entity_factory = EntityFactory()
    repository = entity_factory.entity('unknown', reset_crew_repository)
    assert repository is None


def test_raise_exception_if_invalid_json(invalid_crew):
    entity_factory = EntityFactory()
    with pt.raises(json.decoder.JSONDecodeError):
        entity_factory.entity('crew', invalid_crew)


def test_create_crew_repository(reset_crew_repository):
    entity_factory = EntityFactory()
    repository = entity_factory.entity('crew', reset_crew_repository)
    assert isinstance(repository, CrewRepository)


def test_create_flight_repository(reset_scheduled_flights):
    entity_factory = EntityFactory()
    repository = entity_factory.entity('flights', reset_scheduled_flights)
    assert isinstance(repository, FlightsRepository)
