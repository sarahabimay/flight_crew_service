from google.protobuf import timestamp_pb2 as tspb
import pytest as pt
import src.adapters.incoming.controller as c

class FindCrewRequestFake():
    def __init__(self, params):
        self.location = params['location']
        self.departure_dt = params['departure_dt']
        self.return_dt = params['return_dt']

@pt.fixture
def valid_crew_request():
    departure_ts = tspb.Timestamp()
    departure_ts.FromJsonString('2021-03-17T09:00:00Z')

    return_ts = tspb.Timestamp()
    return_ts.FromJsonString('2021-03-18T09:00:00Z')
    location = 'London'
    return FindCrewRequestFake({
            'location': location,
            'departure_dt': departure_ts,
            'return_dt': return_ts
            })

def test_no_pilot_found_for_bad_depart_date():
    departure_ts = None

    return_ts = tspb.Timestamp()
    return_ts.FromJsonString('2021-03-18T09:00:00Z')

    location = 'Nowhereland'

    request = FindCrewRequestFake({
        'location': location,
        'departure_dt': departure_ts,
        'return_dt': return_ts
        })

    assert c.find_crew_for(request) == None

def test_no_pilot_found_for_bad_return_date():
    departure_ts = tspb.Timestamp()
    departure_ts.FromJsonString('2021-03-17T09:00:00Z')

    return_ts = None

    location = 'Nowhereland'

    request = FindCrewRequestFake({
        'location': location,
        'departure_dt': departure_ts,
        'return_dt': return_ts
        })

    assert c.find_crew_for(request) == None

def test_no_pilot_found(valid_crew_request, mocker):
    mocker.patch(
            'src.adapters.incoming.controller.find_pilot_for',
            return_value = None
            )
    assert c.find_crew_for(valid_crew_request) == None

def test_a_pilot_is_found(valid_crew_request, mocker):
    found_pilot = {
            }

    mocker.patch(
            'src.adapters.incoming.controller.find_pilot_for',
            return_value = {'ID': 1}
            )

    assert c.find_crew_for(valid_crew_request) == c.FindCrewResponse(id=1)

'''
def test_find_crew_request_object_is_sent(valid_crew_request, mocker):
    mock = mocker.MagicMock(
            'src.adapters.incoming.controller.find_pilot_for',
            return_value = None
            )

    expected_departure = arrow.get(valid_crew_request['departure_dt'].ToDatetime())
    expected_return = arrow.get(valid_crew_request['return_dt'].ToDatetime())
    location = valid_crew_request['location']
    expected_request = c.FindCrewRequest(location, expected_departure, expected_return)

    c.find_crew_for(valid_crew_request) == None
    assert mock.assert_called_with(expected_request)
'''

# tests for scheduling a flight for a pilot

class ScheduleCrewRequestFake():
    def __init__(self, params):
        self.pilot_id = params['pilot_id']
        self.location = params['location']
        self.departure_dt = params['departure_dt']
        self.return_dt = params['return_dt']

@pt.fixture
def valid_schedule_request():
    departure_ts = tspb.Timestamp()
    departure_ts.FromJsonString('2021-03-17T09:00:00Z')

    return_ts = tspb.Timestamp()
    return_ts.FromJsonString('2021-03-18T09:00:00Z')
    return ScheduleCrewRequestFake({
            'pilot_id': 12345,
            'location': 'London',
            'departure_dt': departure_ts,
            'return_dt': return_ts
            })

def test_no_flight_scheduled_for_bad_dates(mocker):
    invalid_departure_ts = None
    invalid_return_ts = None
    location = 'Nowhereland'

    request = ScheduleCrewRequestFake({
        'pilot_id': 123,
        'location': location,
        'departure_dt': invalid_departure_ts,
        'return_dt': invalid_return_ts
        })

    mocker.patch(
            'src.adapters.incoming.controller.schedule_flight_for',
            return_value =  {}
            )
    assert c.schedule_crew_for(request) == None

def test_cannot_schedule_a_flight(valid_schedule_request, mocker):
    mocker.patch(
            'src.adapters.incoming.controller.schedule_flight_for',
            return_value = None
            )
    assert c.schedule_flight_for(valid_schedule_request) == None

def test_successfully_schedules_crew_for_a_flight(valid_schedule_request, mocker):
    mocker.patch(
            'src.adapters.incoming.controller.schedule_flight_for',
            return_value = {'ID': 123, 'status': 'Success'}
            )
    assert c.schedule_crew_for(valid_schedule_request) == c.ScheduleCrewResponse(status='Success')
