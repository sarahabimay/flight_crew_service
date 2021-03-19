from pipetools import maybe
from functools import reduce


def find_zero_utilised_pilots(pilots, flights):
    pilot_with_zero_utilisation = None
    for p in pilots:
        if p['ID'] not in flights:
            pilot_with_zero_utilisation = p
            break
    return pilot_with_zero_utilisation


def find_pilot_for(datastore, find_crew_request):
    pilots = datastore.get_pilots_for(find_crew_request.location, find_crew_request.depart_on,
                                      find_crew_request.return_on)
    flights = datastore.get_all_flights_grouped_by_pilot()
    if pilots:
        if len(pilots) == 1 or not flights:
            return pilots.pop(0)
        else:
            pilot_with_zero_utilisation = (flights > maybe
                                           | (lambda f: list(f.keys()))
                                           | (find_zero_utilised_pilots, pilots))
            if pilot_with_zero_utilisation:
                return pilot_with_zero_utilisation

            result = (flights > maybe
                      | pilot_utilisations
                      | (_filter_for_eligible_pilots, pilots)
                      | _take_pilot_with_lowest_utilisation
                      | _format_result
                      )
            return result
    return {}


def pilot_utilisations(all_flights):
    utilisations = {}
    for key, value in all_flights.items():
        if isinstance(value, list):
            count = len(value)
            utilisation = count / _total_flight_count(all_flights)
            utilisations.update({key: utilisation})
    return utilisations


def _total_flight_count(all_flights):
    return sum([len(all_flights[x]) for x in all_flights if isinstance(all_flights[x], list)])


def _filter_for_eligible_pilots(pilots, utilisations):
    pilot_ids = list(map(lambda p: p['ID'], pilots))
    filtered_utes = dict(filter(lambda e: e[0] in pilot_ids, utilisations.items()))
    return filtered_utes


def _take_pilot_with_lowest_utilisation(selected_pilots):
    return list(reduce(lambda x, y: x if x[1] < y[1] else y, selected_pilots.items()))


def _format_result(selected_pilot_id):
    return {'ID': selected_pilot_id[0]}

