import os
from functools import partial

import arrow

from .entity_factory import EntityFactory
from .query_interface import QueryInterface

ISO_DOW_TO_DAY_STRING = {
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
    7: 'Sunday'
}


class JsonDataStore(QueryInterface):
    def __init__(self, entity_config, entity_factory):
        self.repositories = {}
        self._load_entities(entity_config, entity_factory)

    def get_pilots_for(self, base_location, depart_on, return_on):
        if self.repositories:
            departure_day = self._day_of_the_week(depart_on)
            return_day = self._day_of_the_week(return_on)

            by_base_and_dow_part = partial(self._by_location_and_dow,
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

    def get_all_flights_grouped_by_pilot(self):
        if self.repositories:
            flights_by_pilot = {}
            for flight in self._flights_repository().flights():
                key = flight['ID']
                if key not in flights_by_pilot.keys():
                    flights_by_pilot[key] = [flight]
                else:
                    flights_by_pilot[key] += [flight]

            return flights_by_pilot
        return {}

    def schedule_flight_for(self, pilot_id, location, depart_on, return_on):
        flight = {
            'ID': pilot_id,
            'Base': location,
            'DepartureDateTime': depart_on,
            'ReturnDateTime': return_on
        }
        self._flights_repository().append(flight)
        return flight

    def _load_entities(self, entity_config, entity_factory):
        if isinstance(entity_factory, EntityFactory):
            for entity in entity_config:
                entity_name = entity['entity_name']
                location = os.path.expanduser(entity['location'])
                if os.path.exists(location):
                    self.repositories[entity_name] = entity_factory.entity(entity_name, location)
                else:
                    self.repositories = {}
        return self.repositories

    def _crew_repository(self):
        return self.repositories['crew'].crew()

    def _flights_repository(self):
        return self.repositories['flights']

    def _day_of_the_week(self, a_datetime):
        iso_dow = arrow.get(a_datetime).isoweekday()
        return ISO_DOW_TO_DAY_STRING[iso_dow]

    @staticmethod
    def _by_location_and_dow(pilot, location, departure_dow, return_dow):
        if pilot['Base'] == location and departure_dow in pilot['WorkDays'] and return_dow in pilot['WorkDays']:
            return True
        else:
            return False

    def _upcoming_flight(self, pilot_ids, flight):
        if flight['ID'] in pilot_ids and self._future_date(flight['DepartureDateTime']):
            return True
        else:
            return False

    @staticmethod
    def _future_date(datetime):
        return arrow.get(datetime) > arrow.utcnow()

