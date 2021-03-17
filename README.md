Language:
Python

Test:
pytest

API:
gRPC

Datastore:
File store with JSON.

Reason for choices:
* I had been reading about the benefits of RPC over HTTP for microservices api and
  as I haven't ever used gRPC I thought I'd experiment.

* I also have used Python only a little commercially and thought I'd take the opportunity
  to build something from scratch.
  Issues with choices:

* More of a learning curve with Python ecosystem and tooling than I expected! e.g. who knew
  simply importing sibling modules/packages could cause so much headache.
* JSON datastore - if the datastore was an actual database then a lot of the logic could be
  translated into SQL. However with JSON a lot of the data extraction needs to be done
  programmatically.

Assumptions:
* Thre isn't any mention of storing the scheduled flights but I am assuming they would be
* A pilot will only be eligible if they are not on a scheduled flight already
* Will need to calculate the utilisation of each pilot and select the one with the least
* A pilot is eligible if they are working on departure and return days and for a location.
  e.g. if Pilot1 works London, and Wed, Fri, but depart date is a Wed and return date is a
       Thursday, then the Pilot won't be eligible.
* A Pilot is eligible between their already scheduled flights however that could be
  unrealistic to have back to back flights scheduled.  I don't know what the expectations
  are in terms of how many flights they can take in a day and how much time in between, etc
  so to keep it simple I will assume they can work back to back flights.

To generate the gRPC classess and server and client stubs:

```
python -m grpc_tools.protoc -I ./protos --python_out=. --grpc_python_out=.
./protos/crew_service.proto
```

To run the server in one terminal:

```
python crew_service_server.py
```

to run a stub client in another terminal:

```
python crew_service_client.py
```
