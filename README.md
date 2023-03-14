# CET_Go_server
Simple Flask server for project

## Current endpoints

1. /floors/\<code\>
	
	returns the url to svg floormap

1. /floorplan/\<code\>

	returns floormap svg

1. /shortestpath?src=\<room\>&dest=\<room\>

	returns shortest path


## cred.env file format

```sh
# Neo4J credentials
NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
AURA_INSTANCENAME=

# Psql cred
PSQL_USER=
PSQL_DATABASE=
PSQL_PASSWORD=
PSQL_PORT=
PSQL_HOST=
```