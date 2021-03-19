class QueryInterface:
    def get_pilots_for(self, base_location, departure_dt, return_dt) -> list:
        pass

    def get_all_flights_grouped_by_pilot(self) -> dict:
        pass

    def get_upcoming_flights_for(self, pilots) -> list:
        pass

    def schedule_flight_for(self, pilot, location, departure_dt, return_dt) -> dict:
        pass
