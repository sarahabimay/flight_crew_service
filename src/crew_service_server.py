from concurrent import futures
import logging

import grpc

from crew_service_pb2 import PilotResponse, ScheduleConfirmationResponse
from crew_service_pb2_grpc import CrewServiceServicer, add_CrewServiceServicer_to_server
import adapters.incoming.usecases.find_pilot_use_case as find_pilot
# from find_pilot_use_case import find_pilot_for

def get_pilot_for(pilot_id, pilot_db):
    return None

class CrewServiceServicer(CrewServiceServicer):
    def GetPilotFor(self, request, context):
        pilot = find_pilot.find_pilot_for(request.location, request.departure_dt, request.return_dt)
        if pilot is None:
            return PilotResponse(pilot_id="")
        else:
            return pilot

    def ScheduleFlightFor(self, request, context):
        pilot = get_pilot_for(request.pilot_id, "pilot_db")
        if pilot is None:
            return ScheduleConfirmationResponse(status="Not Scheduled")
        else:
            return ScheduleConfirmationResponse(status="Scheduled")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_CrewServiceServicer_to_server(CrewServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
