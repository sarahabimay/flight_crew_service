import arrow
import pytest as pt

import src.adapters.incoming.usecases.schedule_flight_use_case as uc
from src.adapters.incoming.controller import ScheduleCrewRequest


@pt.fixture
def valid_request():
    depart_on = arrow.utcnow().shift(days=1)
    return_on = arrow.utcnow().shift(days=2)
    return ScheduleCrewRequest(1, 'Munich', depart_on, return_on)


@pt.fixture
def ineligible_pilot_request():
    depart_on = arrow.utcnow()
    return_on = arrow.utcnow().shift(days=2)
    return ScheduleCrewRequest(5, 'Ineligible', depart_on, return_on)


@pt.fixture
def clash_with_schedule_request():
    depart_on = arrow.get("2022-06-01T09:00:00Z")
    return_on = arrow.get("2022-06-03T11:00:00Z")
    return ScheduleCrewRequest(1, 'Munich', depart_on, return_on)


@pt.fixture
def dates_passed_request():
    depart_on = arrow.utcnow().shift(months=-11)
    return_on = arrow.utcnow().shift(months=-10)
    return ScheduleCrewRequest(1, 'Munich', depart_on, return_on)


@pt.fixture
def invalid_dates():
    depart_on = arrow.utcnow().shift(hours=+5)
    return_on = arrow.utcnow()
    return ScheduleCrewRequest(1, 'Munich', depart_on, return_on)


class JsonDataStoreFake:
    def __init__(self, pilots=None, pilot_upcoming_flights=None):
        self.upcoming_flights = [{
            "ID": 1,
            "Base": "Munich",
            "DepartureDateTime": "2022-06-01T09:00:00Z",
            "ReturnDateTime": "2022-06-03T11:00:00Z"
        }] if pilot_upcoming_flights is None else pilot_upcoming_flights

        self.pilots = [{'ID': 1}, {'ID': 2}, {'ID': 3}] if pilots is None else pilots
        self.schedule_flight_has_been_called = False

    def get_pilots_for(self, _location, _depart_on, _return_on):
        return self.pilots

    def get_upcoming_flights_for(self, _pilots):
        return self.upcoming_flights

    def schedule_flight_for(self, _pilot, _location, _departure_dt, _return_dt):
        self.schedule_flight_has_been_called = True


def test_does_not_schedule_flight_if_no_datastore(valid_request):
    pilot = uc.schedule_flight_for(None, valid_request)

    assert pilot is None


def test_does_not_schedule_flight_if_no_pilot_found_for_request_params(valid_request):
    pilot = uc.schedule_flight_for(JsonDataStoreFake(pilots=[]), valid_request)

    assert pilot is None


def test_does_not_schedule_flight_when_not_eligible(ineligible_pilot_request):
    datastore = JsonDataStoreFake()

    status = uc.schedule_flight_for(datastore, ineligible_pilot_request)

    assert status is None


def test_schedules_flight_when_eligible(valid_request):
    datastore = JsonDataStoreFake()
    status = uc.schedule_flight_for(datastore, valid_request)

    assert status['status'] is 'Scheduled'
    assert datastore.schedule_flight_has_been_called is True


def test_schedules_flight_when_eligible_and_no_clash(valid_request):
    datastore = JsonDataStoreFake()
    status = uc.schedule_flight_for(datastore, valid_request)

    assert status['status'] == 'Scheduled'
    assert datastore.schedule_flight_has_been_called is True


def test_does_not_schedule_flight_when_clash(clash_with_schedule_request):
    datastore = JsonDataStoreFake()
    status = uc.schedule_flight_for(datastore, clash_with_schedule_request)

    assert status['status'] == 'ScheduleError: Clash'
    assert datastore.schedule_flight_has_been_called is False


def test_does_not_schedule_departure_date_in_past(dates_passed_request):
    datastore = JsonDataStoreFake()
    status = uc.schedule_flight_for(datastore, dates_passed_request)

    expected = 'ScheduleError: InvalidDate'
    assert status['status'] == expected
    assert datastore.schedule_flight_has_been_called is False


def test_does_not_schedule_for_unordered_depart_and_return_date(invalid_dates):
    datastore = JsonDataStoreFake()
    status = uc.schedule_flight_for(datastore, invalid_dates)

    expected = 'ScheduleError: InvalidDate'
    assert status['status'] == expected
    assert datastore.schedule_flight_has_been_called is False
