### Language:
Python

### Test framework:
pytest

### API protocol:
[gRPC](https://grpc.io/docs/languages/python/quickstart/)

### Datastore:
File store with JSON.

## Reasons for choices:
* I had been reading about the benefits of RPC over HTTP for microservices api and
  as I haven't ever used gRPC I thought I'd experiment.

* I also have used Python only a little commercially and thought I'd take the opportunity
  to build something from scratch.
  
### Issues with choices:

* More of a learning curve with Python ecosystem and tooling than I expected! e.g. who knew
  simply importing sibling modules/packages could cause so much headache.
* JSON datastore - if the datastore was an actual database then a lot of the logic could be
  translated into SQL. However with JSON a lot of the data extraction needs to be done
  programmatically.

## Assumptions:
* Specifications don't mention expectations in terms of persisting scheduled flights so I have presumed
    they would need to be.  
        * I am most familiar with relational databases so I went down that route.  Potentially a document style database would have been simpler.
* A pilot will only be eligible if they are already 'registered' in the 'crew  repository' and are not on a scheduled flight already
* Will need to calculate the utilisation of all pilots and select the eligibe pilot with the least utilisation.  This is fairly rudementary and definitely not 'complete' wrt the business requirements.
* A pilot is eligible if the requested departure and return dates are on one of their registered 'Working Days' and one of their 'Base' locations. 
  e.g. if Pilot1 works London, and Wed, Fri, but depart date is a Wed and return date is a
       Thursday, then the Pilot won't be eligible.
* A Pilot is eligible between their already scheduled flights however that could be
  unrealistic to have back to back flights scheduled.  I don't know what the expectations
  are in terms of how many flights they can take in a day and how much time in between, etc
  so to keep it simple I will assume they can work back to back flights.

## Known Issues

I'm sure there are many! I've dotted one or two 'TODO's around, but there are plenty of 'little things' here and there.
* Makefile doesn't source the env vars
* remaining console prints should be 'logging' messages instead
* configuration for dev should be improved
* some test dates need to be tightened up as will cause a test or two to break in a year or two.
* Unit tests only.  Only manual tests done with the stub and not all use cases tested end to end.
* I'm sure there are plenty of python idiomatic lines I've crossed.

#### To generate the gRPC classess and server and client stubs:
After installing gprc libraries as per installation [instruction](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#links).

```
python -m grpc_tools.protoc -I ./protobufs --python_out=./src --grpc_python_out=./src
./protobufs/crew_service.proto
```

### To run:
Export environment variables to export as `make dev` wasn't working:
```
export FLIGHTS_REPOSITORY=/your/path/to/cloned/repo/flight_crew_service/repository/flights.json
export CREW_REPOSITORY=/your/path/to/cloned/repo/flight_crew_service/repository/crew.json
export DATASTORE=json_type

```
Run the server in one terminal:

```
> git clone <repository>
> cd <repository>
> pipenv shell
> pipenv install
> make dev --> skip for now as this was supposed to export the env vars, but wassn't working at the time of zip.

python src/crew_service_server.py
```

Run a stub client in another terminal:

```
python src/crew_service_client.py
```

Note: this stub just tests one scenario!

### Tests 

Only had time for unit tests:

```
> python -m pytest test
```
