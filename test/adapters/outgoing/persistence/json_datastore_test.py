import arrow
import json
import pytest as pt

from src.adapters.outgoing.persistence.entity_factory import EntityFactory
from src.adapters.outgoing.persistence.json_datastore import JsonDataStore

from fixtures.repository import skeleton_crew, scheduled_flights, db_path, invalid_crew, flights_history


@pt.fixture()
def factory():
    return EntityFactory()


@pt.fixture()
def valid_datastore(skeleton_crew, scheduled_flights, factory):
    return JsonDataStore(
        [{'entity_name': 'crew', 'location': skeleton_crew},
         {'entity_name': 'flights', 'location': scheduled_flights}],
        factory)


@pt.fixture
def find_daphne():
    return {
        'depart_on': arrow.get('2020-05-01T09:00:00Z'),
        'return_on': arrow.get('2020-05-03T11:00:00Z'),
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
        'depart_on': arrow.get('2020-05-02T09:00:00Z'),
        'return_on': arrow.get('2020-05-03T11:00:00Z'),
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


@pt.fixture
def with_flight_history(skeleton_crew, flights_history, factory):
    return JsonDataStore(
        [{'entity_name': 'crew', 'location': skeleton_crew},
         {'entity_name': 'flights', 'location': flights_history}],
        factory)


class TestJsonDataStore:
    def test_does_not_load_any_repositories(self, factory):
        json_datastore = JsonDataStore([], factory)
        assert json_datastore.repositories == {}

    def test_does_not_load_any_repositories_without_factory(self, skeleton_crew):
        json_datastore = JsonDataStore(
            [{'entity_name': 'crew', 'location': skeleton_crew}],
            None)
        assert json_datastore.repositories == {}

    def test_raise_exception_if_invalid_json(self, factory, invalid_crew):
        with pt.raises(json.decoder.JSONDecodeError):
            JsonDataStore(
                [{'entity_name': 'crew', 'location': invalid_crew}],
                factory)

    def test_load_entities(self, valid_datastore):
        assert valid_datastore.repositories is not {}

    def test_does_not_find_pilots(self, valid_datastore):
        pilots = valid_datastore.get_pilots_for(
            'Alabama',
            arrow.get('2020-05-01T09:00:00Z'),
            arrow.get('2020-05-03T11:00:00Z')
        )
        assert pilots == []

    def test_get_single_pilot_for_location_and_dates(self, valid_datastore, find_daphne):
        pilots = valid_datastore.get_pilots_for(
            find_daphne['base_location'],
            find_daphne['depart_on'],
            find_daphne['return_on'])
        assert pilots == find_daphne['expected']

    def test_get_multiple_pilot_for_location_and_dates(self, valid_datastore, find_multiple):
        pilots = valid_datastore.get_pilots_for(
            find_multiple['base_location'],
            find_multiple['depart_on'],
            find_multiple['return_on'])
        assert pilots == find_multiple['expected']

    def test_does_not_find_any_upcoming_flights_for_pilot(self, valid_datastore):
        assert valid_datastore.get_upcoming_flights_for(pilots=[5]) == []

    def test_finds_upcoming_flights_for_pilot(self, valid_datastore):
        expected = [{
            "ID": 3,
            "Base": "Munich",
            "DepartureDateTime": "2022-06-01T09:00:00Z",
            "ReturnDateTime": "2022-06-03T11:00:00Z"
        }]
        assert valid_datastore.get_upcoming_flights_for(pilots=[3]) == expected

    def test_get_all_flights_by_pilot(self, with_flight_history):
        expected = {
            1: [{'Base': 'Munich', 'ID': 1}, {'Base': 'Berlin', 'ID': 1}],
            3: [{'Base': 'Munich', 'ID': 3}]
        }
        assert with_flight_history.get_all_flights_grouped_by_pilot() == expected

    def test_schedule_flight_successfully(self, valid_datastore):
        expected_flight = {
            "ID": 2,
            "Base": "Munich",
            "DepartureDateTime": "2021-12-01T09:00:00Z",
            "ReturnDateTime": "2021-12-03T11:00:00Z"
        }
        expected = {
            "ID": 2,
            "Base": "Munich",
            "DepartureDateTime": "2021-12-01T09:00:00Z",
            "ReturnDateTime": "2021-12-03T11:00:00Z"
        }
        assert valid_datastore.schedule_flight_for(pilot_id=2,
                                                   location='Munich',
                                                   depart_on="2021-12-01T09:00:00Z",
                                                   return_on="2021-12-03T11:00:00Z") == expected
        assert valid_datastore.get_upcoming_flights_for(pilots=[2]) == [expected_flight]

