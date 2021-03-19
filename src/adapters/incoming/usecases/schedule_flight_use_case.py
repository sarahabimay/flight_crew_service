import arrow


# TODO : This and the other use case feel like they should be a class as 'datastore' is passed around and one function
# references another

def schedule_flight_for(datastore, schedule_flight_request):
    if datastore:
        pilot_id = schedule_flight_request.pilot_id
        location = schedule_flight_request.location
        depart_on = schedule_flight_request.depart_on
        return_on = schedule_flight_request.return_on

        pilots = datastore.get_pilots_for(location, depart_on, return_on)
        if pilot_id in list(map(lambda p: p['ID'], pilots)):
            if _any_clashes_for(pilot_id, depart_on, return_on, datastore):
                return {'status': 'ScheduleError: Clash'}
            if _invalid_dates(depart_on, return_on):
                return {'status': 'ScheduleError: InvalidDate'}
            return _schedule_flight_for(datastore, pilot_id, location, depart_on, return_on)
        else:
            return {'status': 'Unscheduled: Unknown Pilot'}

    return None


def _invalid_dates(depart_on, return_on):
    depart_on = arrow.get(depart_on)
    return_on = arrow.get(return_on)

    return depart_on < arrow.utcnow() or return_on < depart_on


def _any_clashes_for(pilot, depart_on, return_on, datastore):
    upcoming_flights = datastore.get_upcoming_flights_for([pilot])
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


def _schedule_flight_for(datastore, pilot, location, departure_dt, return_dt):
    depart_on = arrow.get(departure_dt)
    return_on = arrow.get(return_dt)

    if depart_on < arrow.utcnow() or return_on < depart_on:
        return {'status': 'ScheduleError: InvalidDate'}

    datastore.schedule_flight_for(pilot, location, depart_on, return_on)
    return {'status': 'Scheduled'}
