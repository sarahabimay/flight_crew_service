import os
from functools import partial

import arrow

from .entity_factory import EntityFactory
from .query_interface import QueryInterface


def _by_location_and_dow(pilot, location, departure_dow, return_dow):
    if pilot['Base'] == location and departure_dow in pilot['WorkDays'] and return_dow in pilot['WorkDays']:
        return True
    else:
        return False


class JsonDataStore(QueryInterface):
    def __init__(self, entity_config, entity_factory):
        self.repositories = {}
        self.load_entities(entity_config, entity_factory)

    def load_entities(self, entity_config, entity_factory):
        if isinstance(entity_factory, EntityFactory):
            for entity in entity_config:
                entity_name = entity['entity_name']
                location = os.path.expanduser(entity['location'])
                if os.path.exists(location):
                    self.repositories[entity_name] = entity_factory.entity(entity_name, location)
                else:
                    self.repositories = {}
        return self.repositories

    def get_pilots_for(self, base_location, departure_dt, return_dt):
        if self.repositories:
            departure_day = self._day_of_the_week(departure_dt)
            return_day = self._day_of_the_week(return_dt)

            by_base_and_dow_part = partial(_by_location_and_dow,
                                           location=base_location,
                                           departure_dow=departure_day,
                                           return_dow=return_day)
            return list(filter(by_base_and_dow_part, self._crew_repository()))
        return []

    def get_upcoming_flights_for(self, pilots):
        if self.repositories:
            upcoming_flights_part = partial(self._upcoming_flight, pilots)
            return list(filter(upcoming_flights_part, self._flights_repository().flights()))
        return []

    def schedule_flight_for(self, pilot, location, departure_dt, return_dt):
        depart_on = arrow.get(departure_dt)
        return_on = arrow.get(return_dt)
        if depart_on < arrow.utcnow() or return_on < depart_on:
            return {'status': 'ScheduleError: InvalidDate'}
        elif self._any_clashes_for(pilot, depart_on, return_on):
            return {'status': 'ScheduleError: Clash'}
        else:
            flight = {
                'ID': pilot,
                'Base': location,
                'DepartureDateTime': departure_dt,
                'ReturnDateTime': return_dt
            }
            self._flights_repository().append(flight)
            return {
                'status': 'Scheduled',
                'flight': flight
            }

    def _crew_repository(self):
        return self.repositories['crew'].crew()

    def _flights_repository(self):
        return self.repositories['flights']

    def _day_of_the_week(self, a_datetime):
        ISO_DOW_TO_DAY_STRING = {
            1: 'Monday',
            2: 'Tuesday',
            3: 'Wednesday',
            4: 'Thursday',
            5: 'Friday',
            6: 'Saturday',
            7: 'Sunday'
        }
        iso_dow = arrow.get(a_datetime).isoweekday()
        return ISO_DOW_TO_DAY_STRING[iso_dow]

    def _upcoming_flight(self, pilot_ids, flight):
        if flight['ID'] in pilot_ids and self._future_date(flight['DepartureDateTime']):
            return True
        else:
            return False

    def _future_date(self, datetime):
        return arrow.get(datetime) > arrow.utcnow()

    def _any_clashes_for(self, pilot, depart_on, return_on):
        upcoming_flights = self.get_upcoming_flights_for([pilot])
        for flight in upcoming_flights:
            flight_depart = arrow.get(flight['DepartureDateTime'])
            flight_return = arrow.get(flight['ReturnDateTime'])
            if (
                    flight_depart < depart_on < flight_return
                    or flight_depart < return_on < flight_return
                    or depart_on <= flight_depart and flight_return <= return_on
            ):
                return True

        return False