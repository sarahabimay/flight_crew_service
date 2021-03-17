import grpc

import datetime

from google.protobuf import timestamp_pb2

from crew_service_pb2 import DateTimeLocationRequest, PilotLocationDatetimePeriodRequest
from crew_service_pb2_grpc import CrewServiceStub

channel = grpc.insecure_channel('localhost:50051')
stub = CrewServiceStub(channel)

# Convert datetime string to grpc Timestamp
timestamp_instance = timestamp_pb2.Timestamp()
timestamp_instance.FromJsonString('2020-05-01T09:00:00Z')
departure_dt = timestamp_instance
print("Departure time:")
print(departure_dt.ToJsonString())

# Convert datetime string to grpc Timestamp
timestamp_instance.FromJsonString('2020-05-01T11:00:00Z')
return_dt = timestamp_instance
print("Return time:")
print(return_dt.ToJsonString())

location_and_period = DateTimeLocationRequest(
        location='Munich',
        departure_dt=departure_dt,
        return_dt=return_dt)

pilot_response = stub.GetPilotFor(location_and_period)
if pilot_response.pilot_id:
    print("Pilot available for location and time period: %s" % (pilot_response.pilot_id))
else:
    print("No pilot found for given location and time period")

pilot_and_period = PilotLocationDatetimePeriodRequest(
        pilot_id="123",
        departure_dt=departure_dt,
        return_dt=return_dt)

schedule_response = stub.ScheduleFlightFor(pilot_and_period)
if schedule_response.status == "Scheduled":
    print("Pilot scheduled for flight in a time period: %s" % (pilot_response.pilot_id))
else:
    print("No flight scheduled for given pilot and time period")
