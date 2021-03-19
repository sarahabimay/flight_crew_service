import arrow
import pytest as pt

import src.adapters.incoming.usecases.find_pilot_use_case as uc
from src.adapters.incoming.controller import FindCrewRequest


@pt.fixture
def valid_request():
    depart_on = arrow.utcnow()
    return_on = arrow.utcnow().shift(days=2)
    return FindCrewRequest('Munich', depart_on, return_on)


class JsonDataStoreFake:
    def __init__(self, pilots=None, all_flights_by_pilot=None):
        self.all_flights_by_pilot = {
            1: [{}, {}, {}],
            2: [{}, {}],
            3: [{}],
            4: [{}, {}, {}, {}],
        } if all_flights_by_pilot is None else all_flights_by_pilot

        self.pilots = [{'ID': 1}, {'ID': 2}, {'ID': 3}] if pilots is None else pilots

    def get_pilots_for(self, _location, _depart_on, _return_on):
        return self.pilots

    def get_all_flights_grouped_by_pilot(self):
        return self.all_flights_by_pilot


def test_no_pilots_found_for_request_params(valid_request):
    pilots_for_request = []

    pilot = uc.find_pilot_for(JsonDataStoreFake(pilots=pilots_for_request), valid_request)

    assert pilot == {}


def test_selects_only_pilot_found(valid_request):
    pilots_for_request = [
        {
            'ID': 2
        }
    ]

    pilot = uc.find_pilot_for(JsonDataStoreFake(pilots=pilots_for_request), valid_request)

    assert pilot == {'ID': 2}


def test_selects_first_pilot_if_no_flights_data(valid_request):
    pilots_for_request = [
        {
            'ID': 1
        },
        {
            'ID': 2
        }
    ]

    pilot = uc.find_pilot_for(JsonDataStoreFake(pilots=pilots_for_request, all_flights_by_pilot={}), valid_request)

    assert pilot == {'ID': 1}


def test_selects_first_pilot_unutilised(valid_request):
    pilots_for_request = [
        {
            'ID': 1
        },
        {
            'ID': 2
        },
        {
            'ID': 3
        }
    ]

    all_flights_by_pilot = {1: [{'ID': 1}]}
    pilot = uc.find_pilot_for(JsonDataStoreFake(pilots=pilots_for_request, all_flights_by_pilot=all_flights_by_pilot), valid_request)

    expected_pilot_with_no_utilisation = {'ID': 2}
    assert pilot == expected_pilot_with_no_utilisation


def test_selects_pilot_with_least_utilisation(valid_request):
    pilots_for_request = [
        {
            'ID': 1
        },
        {
            'ID': 2
        }
    ]

    flights_by_pilot = {
        1: [
            {'ID': 1},
            {'ID': 1},
            {'ID': 1}
        ],
        2: [
            {'ID': 2},
            {'ID': 2}
        ]
    }

    pilot = uc.find_pilot_for(JsonDataStoreFake(pilots=pilots_for_request, all_flights_by_pilot=flights_by_pilot), valid_request)

    expected_pilot_with_least_utilisation = {'ID': 2}
    assert pilot == expected_pilot_with_least_utilisation

