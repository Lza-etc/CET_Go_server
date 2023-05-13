# CET_Go_server
Simple Flask server for project

## Current endpoints

1. /floors/\<code\>
	
	returns the url to svg floormap

1. /floorplan/\<code\>

	returns floormap svg

1. /shortestpath?src=\<room\>&dest=\<room\>

	returns shortest path

	Values needed:

		1. src

		1. dest

		1. dept

1. /login and /logout 

	For event creators to log in to create / modify events

	Values needed
	
		1. username

		1. password

1. /events 
	
	GET : returns all events
	
	POST: allows to create and modify events (Requires Login)

		Values needed:

			1. id: user id of creator

			1. Operation: Create/List/Update/Delete

			1. data for the event

1. /organizer/\<code\>

	For Uploading and retrieving details of event organizers

	GET: Receive public info of organizer

	POST: Receive all info of organizer (Login required)
		Also ability to update


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
