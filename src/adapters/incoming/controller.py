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

def validate(request):
    return request

def convert_datetimes(request):
    try:
        depart_on = arrow.get(request['departure_dt'].ToDatetime())
        return_on = arrow.get(request['return_dt'].ToDatetime())
        request.update({
                'departure_dt': depart_on,
                'return_dt': return_on,
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


def find_crew_for(request):
    pilot = (request > maybe
            | validate
            | convert_datetimes
            | _find_crew_request
            | find_pilot_for
            )

    if pilot:
        return FindCrewResponse(id=pilot['ID'])

    return None

def schedule_crew_for(request):
    flight = (request > maybe
            | validate
            | convert_datetimes
            | _schedule_crew_request
            | schedule_flight_for
            )

    if flight:
        return ScheduleCrewResponse(status=flight['status'])

    return None
