MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
JSON_DB_PATH := ${MAKEFILE_PATH}/repository

.PHONY: dev

.EXPORT_ALL_VARIABLES:

CREW_REPOSITORY = ${JSON_DB_PATH}/crew.json
FLIGHTS_REPOSITORY = ${JSON_DB_PATH}/flights.json
DATASTORE = json_type

dev:
	@echo $$CREW_REPOSITORY $$FLIGHT_REPOSITORY $$DATASTORE
