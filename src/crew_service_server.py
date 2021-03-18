from concurrent import futures

from crew_service_pb2 import PilotResponse, ScheduleConfirmationResponse
from crew_service_pb2_grpc import CrewServiceServicer, add_CrewServiceServicer_to_server

import grpc
import logging
from adapters.incoming.controller import find_crew_for, schedule_crew_for

class CrewServiceServicer(CrewServiceServicer):
    def GetPilotFor(self, request, context):
        print("Find pilot for ", request.location, request.departure_dt, request.return_dt)

        pilot = find_crew_for(request)
        if pilot is None:
            return PilotResponse(pilot_id="")
        else:
            return PilotResponse(pilot_id=pilot.id)

    def ScheduleFlightFor(self, request, context):
        pilot = schedule_crew_for(request)
        if pilot is None:
            return ScheduleConfirmationResponse(status="Not Scheduled")
        else:
            return ScheduleConfirmationResponse(pilot.status)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_CrewServiceServicer_to_server(CrewServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
