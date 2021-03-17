import json
import os
import sys
import arrow
from functools import partial

from src.adapters.outgoing.persistence.repository import Repository

class FlightsRepository(Repository):
    def __init__(self, location):
        Repository.__init__(self, location)

    def get_upcoming_flights_for(self, pilots):
        self.load(self.location)

        upcoming_flights_part = partial(self._upcoming_flight, pilots)
        return list(filter(upcoming_flights_part, self.db))

    def _upcoming_flight(self, pilot_ids, flight):
        print('next flight', flight)
        if flight['ID'] in pilot_ids and self._future_date(flight['DepartureDateTime']):
            return True
        else:
            return False

    def _future_date(self, datetime):
        return arrow.get(datetime) > arrow.utcnow()

    def schedule_flight_for(self, pilot, location, departure_dt, return_dt):
        depart_on = arrow.get(departure_dt)
        return_on = arrow.get(return_dt)
        if depart_on < arrow.utcnow() or return_on < depart_on:
            return {'status': 'ScheduleError: InvalidDate'}
        elif self._any_clashes_for(pilot, location, depart_on, return_on):
            return {'status': 'ScheduleError: Clash'}
        else:
            flight = {
                    'ID': pilot,
                    'Base': location,
                    'DepartureDateTime': departure_dt,
                    'ReturnDateTime': return_dt
                    }
            self.db.append(flight)
            self.writedb()
            return {
                    'status': 'Scheduled',
                    'flight': flight
                    }

    def _any_clashes_for(self, pilot, location, depart_on, return_on):
        upcoming_flights = self.get_upcoming_flights_for([pilot])
        for flight in upcoming_flights:
            flight_depart = arrow.get(flight['DepartureDateTime'])
            flight_return = arrow.get(flight['ReturnDateTime'])
            if (
                    flight_depart < depart_on and depart_on < flight_return
                    or flight_depart < return_on and return_on < flight_return
                    or depart_on <= flight_depart and flight_return <= return_on
            ):
                return True

        return False
