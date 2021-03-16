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
