import sys
from collections import namedtuple
from functools import partial

import arrow
from pipetools import maybe

from .usecases.find_pilot_use_case import find_pilot_for
from .usecases.schedule_flight_use_case import schedule_flight_for

FindCrewRequest = namedtuple('FindCrewRequest', ['location', 'depart_on', 'return_on'])
FindCrewResponse = namedtuple('FindCrewResponse', ['id'])
ScheduleCrewRequest = namedtuple('FindCrewRequest', ['pilot_id', 'location', 'depart_on', 'return_on'])
ScheduleCrewResponse = namedtuple('FindCrewResponse', ['status'])


class Controller():
    def __init__(self, datastore):
        self.datastore = datastore

    def find_crew_for(self, request):
        pilot = (request > maybe
                 | self._validate
                 | self._find_crew_params
                 | self._convert_datetimes
                 | self._find_crew_request
                 | partial(find_pilot_for, self.datastore)
                 )

        if pilot:
            return FindCrewResponse(id=pilot['ID'])

        return None

    def schedule_crew_for(self, request):
        flight = (request > maybe
                  | self._validate
                  | self._schedule_crew_params
                  | self._convert_datetimes
                  | self._schedule_crew_request
                  | partial(schedule_flight_for, self.datastore)
                  )

        if flight:
            return ScheduleCrewResponse(status=flight['status'])

        return None

    @staticmethod
    def _validate(request):
        return request

    @staticmethod
    def _find_crew_params(request):
        converted_request = {}
        converted_request['location'] = request.location
        converted_request['departure_dt'] = request.departure_dt
        converted_request['return_dt'] = request.return_dt
        return converted_request

    def _schedule_crew_params(self, request):
        converted_request = self._find_crew_params(request)
        converted_request.update({'pilot_id': request.pilot_id})
        return converted_request

    @staticmethod
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

    @staticmethod
    def _find_crew_request(request):
        depart_on = request['departure_dt']
        return_on = request['return_dt']
        location = request['location']
        return FindCrewRequest(location=location, depart_on=depart_on, return_on=return_on)

    @staticmethod
    def _schedule_crew_request(request):
        pilot_id = request['pilot_id']
        depart_on = request['departure_dt']
        return_on = request['return_dt']
        location = request['location']
        return ScheduleCrewRequest(
            pilot_id=pilot_id,
            location=location,
            depart_on=depart_on,
            return_on=return_on)
