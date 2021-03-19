from concurrent import futures

import grpc
import logging
import os

from adapters.incoming.controller import Controller
from adapters.outgoing.persistence.entity_factory import EntityFactory
from adapters.outgoing.persistence.json_datastore import JsonDataStore
from crew_service_pb2 import ScheduleConfirmationResponse, PilotResponse
from crew_service_pb2_grpc import add_CrewServiceServicer_to_server, CrewServiceServicer


class CrewServiceServicer(CrewServiceServicer):
    def __init__(self):
        datastore = os.environ['DATASTORE'] if 'DATASTORE' in os.environ else None
        if datastore == 'json_type':
            print("Crew service will use a JSON data store")
            config = []
            config.append({'entity_name': 'crew',
                           'location': os.environ['CREW_REPOSITORY']}) if 'CREW_REPOSITORY' in os.environ else None
            config.append({'entity_name': 'flights', 'location': os.environ[
                'FLIGHTS_REPOSITORY']}) if 'FLIGHTS_REPOSITORY' in os.environ else None

            self.controller = Controller(JsonDataStore(config, EntityFactory()))
        else:
            self.controller = None

    def GetPilotFor(self, request, context):
        print("Find pilot for location: {}, departure date: {} and return date: {} ".format(
            request.location,
            request.departure_dt.ToJsonString(),
            request.return_dt.ToJsonString()))

        pilot = self.controller.find_crew_for(request)
        if pilot is None:
            return PilotResponse(pilot_id="")
        else:
            return PilotResponse(pilot_id=str(pilot.id))

    def ScheduleFlightFor(self, request, context):
        print("Schedule flight for pilot_id={}, location={}, depart date={}, return date={}".format(
            request.pilot_id,
            request.location,
            request.departure_dt.ToJsonString(),
            request.return_dt.ToJsonString()))

        pilot = self.controller.schedule_crew_for(request)
        if pilot is None:
            return ScheduleConfirmationResponse(status="Not Scheduled")
        else:
            return ScheduleConfirmationResponse(status=pilot.status)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_CrewServiceServicer_to_server(CrewServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
