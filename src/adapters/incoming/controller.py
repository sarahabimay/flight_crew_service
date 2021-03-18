from src.adapters.incoming.usecases.find_pilot_use_case import find_pilot_for
from src.adapters.incoming.usecases.schedule_flight_use_case import schedule_flight_for
from pipetools import pipe, maybe
from collections import namedtuple
import arrow
import sys

FindCrewRequest = namedtuple('FindCrewRequest', ['location', 'depart_on', 'return_on'])
FindCrewResponse = namedtuple('FindCrewResponse', ['id'])
ScheduleCrewRequest = namedtuple('FindCrewRequest', ['pilot_id', 'location', 'depart_on', 'return_on'])
ScheduleCrewResponse = namedtuple('FindCrewResponse', ['status'])

def find_crew_for(request):
    pilot = (request > maybe
            | _validate
            | _find_crew_params
            | _convert_datetimes
            | _find_crew_request
            | find_pilot_for
            )

    if pilot:
        return FindCrewResponse(id=pilot['ID'])

    return None

def schedule_crew_for(request):
    flight = (request > maybe
            | _validate
            | _schedule_crew_params
            | _convert_datetimes
            | _schedule_crew_request
            | schedule_flight_for
            )

    if flight:
        return ScheduleCrewResponse(status=flight['status'])

    return None

def _validate(request):
    return request

def _find_crew_params(request):
    converted_request = {}
    converted_request['location'] = request.location
    converted_request['departure_dt'] = request.departure_dt
    converted_request['return_dt'] = request.return_dt
    return converted_request

def _schedule_crew_params(request):
    converted_request = _find_crew_params(request)
    converted_request.update({'pilot_id': request.pilot_id})
    return converted_request

def _convert_datetimes(request):
    try:
        depart_on = arrow.get(request['departure_dt'].ToDatetime())
        return_on = arrow.get(request['return_dt'].ToDatetime())
        request.update({
            'departure_dt': depart_on,
            'return_dt': return_on
            })
        return request
    except:
        print("exception:", sys.exc_info())
        return None

def _find_crew_request(request):
    depart_on = request['departure_dt']
    return_on = request['return_dt']
    location = request['location']
    return FindCrewRequest(location = location, depart_on = depart_on, return_on = return_on)

def _schedule_crew_request(request):
    pilot_id = request['pilot_id']
    depart_on = request['departure_dt']
    return_on = request['return_dt']
    location = request['location']
    return ScheduleCrewRequest(
            pilot_id = pilot_id,
            location = location,
            depart_on = depart_on,
            return_on = return_on)

