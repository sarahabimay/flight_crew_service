import json
import os
import sys
import arrow
from functools import partial

from src.adapters.outgoing.persistence.repository import Repository

class CrewRepository(Repository):
    def __init__(self, location):
        Repository.__init__(self, location)

    def get_pilots_for(self, base_location, departure_dt, return_dt):
        self.load(self.location)
        departure_day = self._day_of_the_week(departure_dt)
        return_day = self._day_of_the_week(return_dt)

        by_base_and_dow_part = partial(self._by_location_and_dow,
                    location = base_location,
                    departure_dow = departure_day,
                    return_dow = return_day)
        return list(filter(by_base_and_dow_part, self.db['Crew']))

    def _by_location_and_dow(self, pilot, location, departure_dow, return_dow):
        if pilot['Base'] == location and departure_dow in pilot['WorkDays'] and return_dow in pilot['WorkDays']:
            return True
        else:
            return False

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
