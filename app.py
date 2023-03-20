from flask import Flask, jsonify, request, send_file
from flask_restful import Resource, Api
from dotenv import dotenv_values
# from PIL import Image
# requires neo4j module to run query directly from this script
from neo4j import GraphDatabase
import psycopg2 as psql
import json

resources = {
    "floorMaps": {
        "CE": ['https://github.com/HariSK20/CETGo_Data/raw/main/CE0.png', 'https://github.com/HariSK20/CETGo_Data/raw/main/CE1.png', ], 
        "CSE": ['https://github.com/HariSK20/CETGo_Data/raw/main/cs0.svg', 'https://raw.githubusercontent.com/HariSK20/CETGo_Data/main/cs1.svg', 'https://github.com/HariSK20/CETGo_Data/raw/main/cs2.svg'],
        "MCA": ['none exists!']
    }
}

# get credentials
config = dict(dotenv_values("../cred.env"))
# print(config)
# graph db
neo4j_uri_to_server = config["NEO4J_URI"]
neo4j_usr = config["NEO4J_USERNAME"]
neo4j_pwd = config["NEO4J_PASSWORD"]
# psql 
psql_usr = config["PSQL_USER"]
psql_pass = config["PSQL_PASSWORD"]
psql_db = config["PSQL_DATABASE"]
psql_port = config["PSQL_PORT"]
psql_host = config["PSQL_HOST"]


# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)

conn = psql.connect(dbname=psql_db, user=psql_usr, password=psql_pass, host=psql_host, port=psql_port)
# making a class for a particular resource
# the get, post methods correspond to get and post requests
# they are automatically mapped by flask_restful.
# other methods include put, delete, etc.
class Welcome(Resource):
    def get(self):
        return(jsonify({'message': 'HELLO!!'}))


class FloorMap(Resource):
    def get(self, code):
        global conn
        res = {'src': resources['floorMaps'][code[:-1].upper()][int(code[-1])]}
        cur = conn.cursor()
        res['rooms'] = []
        cur.execute("SELECT id,val FROM room_details where z='{}'".format(code[-1]))
        for i in cur.fetchall():
            res['rooms'].append({'ID': i[0], 'Description': i[1]})
        cur.close()
        return jsonify(res)
    # Corresponds to POST request
    def post(self):
        data = request.get_json()     # status code
        return jsonify({'data': data}), 201


class FloorMapFile(Resource):
    def get(self, code):
        path = '../CETGo_Data/'+ code + '.svg'
        return send_file(path, mimetype='image/svg+xml')


class Graph(Resource):
    def post(self):
        data = dict(request.get_json())
        print(data)
        result = []
        if(data == None):
            return(jsonify({'message': 'No data found'}))
        graphDB_Driver  = GraphDatabase.driver(neo4j_uri_to_server, auth=(neo4j_usr, neo4j_pwd))
        with graphDB_Driver.session() as graphDB_Session:
            with conn.cursor() as cur:
                # check if both starting and destination points are in the db first
                cur.execute("select id from {} where id='{}' or id='{}'".format(data['dept'], data['src'], data['dest']))
                s = cur.fetchall()
                if(len(s) != 2):
                    message = ''
                    yes= [0, 0]
                    for i in s:
                        if(i[0] == data['src']):
                            yes[0] = 1
                        elif(i[0] == data['dest']):
                            yes[1] = 1
                    message = "Unable to find {} {} in {}".format("" if yes[0] == 1 else data['src'], "" if yes[1] == 1 else data['dest'], data['dept'])
                    return(jsonify({'Error': 'Invalid rooms!', 'message': message}))
                # checking if the nodes where returned correctly
                query = "match (p1:room {{id: '{0}'}}), (p2:room {{id: '{1}'}}), path = shortestPath((p1)-[*..15]-(p2)) return path".format(data['src'], data['dest'])
                res = graphDB_Session.run(query)
                # for i in list(res):
                #     print(i.data())
                # print(list(res.data()))
                query = "select id, val, fx, fy from {} where id=".format(data['dept'])
                dc = res.data()[0]
                for i in dc['path']:
                    if( not isinstance(i, dict)):
                        continue
                    # because using tupled call of cur.execute is giving error
                    q2 = query[:] + "'{}'".format(i['id'])
                    # cur.execute(query, (str(i['id'])))
                    cur.execute(q2)
                    q = cur.fetchone()
                    if(q == None):
                        return jsonify({'Error': "Unable to find room", 'message': 'Unable to find {} in {}.'.format(i['id'], data['dept'])})
                    result.append({'id': i['id'], 'desc': q[1].strip(), 'fx': str(q[2]), 'fy': str(q[3])})
                    # print(result)
                data['path'] = result
        graphDB_Driver.close()
        return(jsonify(data))

class Event(Resource):
    def get(self):
        data = {}
        # data = request.get_json()     # status code
        # # message = "received"
        # if('List' in data.keys()):
        with conn.cursor() as cur:
            cur.execute("select * from events where id not in ('1')")
            res = cur.fetchall()
            result = {}
            data['count'] = len(res)
            data['events'] = []
            for i in res:
                data['events'].append({'event_id': i[0], 'datetime':i[2], 'description': i[3], 'location':i[4], 'event_name':i[5]})
        # else:
            # data['Error'] = 'Invalid request!'
        return(jsonify(data)) 

    def post(self):
        """ 
            Handles create event. 
                Data taken from body of request
                Required fields to create event: 
                    1. id : id of user creating event
                    2. Operation = "Create" : tells function to create the event
                    3. datetime : the date and time along with timezone of the scheduled event
                    4. event_name : name of the event (max 50 chars)
                    5. description : event description (Max 100 chars)
                    6. location : where the event is happening, usually a room in a department
        """
        data = request.get_json()     # status code
        message = "received"
        if('List' in data.keys()):
            with conn.cursor() as cur:
                cur.execute("select * from events where id not in ('1')")
                res = cur.fetchall()
                result = {}
                data['count'] = len(res)
                data['events'] = []
                for i in res:
                    data['events'].append({'event_id': i[0], 'datetime':i[2], 'description': i[3], 'location':i[4], 'event_name':i[5]})
            return(jsonify(data)) 
        elif('id' in data.keys() and 'Operation' in data.keys()):
            # to be used after login code is complete
            # if(data['id'] != current_user.id):
            #     return( jsonify({'Error': 'Unauthorized user!', 'message': 'User id in request does not match user id of logged in user'}))
            with conn.cursor() as cur:
                # verify valid user
                cur.execute("select id from users where id='{}'".format(data['id']))
                if(cur.fetchone() == None):
                    return jsonify({'Error': 'Invalid user ID', 'message': 'User ID not found!'})

                if(data['Operation'] == 'Create'):
                    # get new event_id
                    cur.execute("Select max(event_id) from events")
                    event_id = int(cur.fetchone()[0]) + 1
                
                    # check if event with same name already exists
                    cur.execute("select event_id from events where event_name='{}'".format(data['event_name']))
                    if(cur.fetchone() is not None):
                        return jsonify({'Error': 'Unable to create Event', 'message': 'Event with same name already exists!'})
                
                    # if all checks successful, inserting event
                    insert_query = "INSERT INTO events VALUES(%s, %s, %s, %s, %s, %s)"
                    cur.execute(insert_query, (event_id, data['id'], data['datetime'], data['description'], data['location'], data['event_name']))
                    # check if insertion was successful
                    if(cur.rowcount > 0):
                        print("successful insertion of event {}".format(event_id))
                        # commit the transaction
                        conn.commit()
                        return( jsonify({'message': 'Event {} successfully created!'.format(event_id)}))
                    else:
                        message = "Unable to create event '{}'!".format(data['event_name'])

                elif(data['Operation'] == 'Update'):
                    message = 'Update not yet available for use'
                    pass
                elif(data['Operation'] == 'Delete'):
                    message = 'Delete not yet available for use'
                    pass 
        return jsonify({'data': data, 'message': message}), 201
        

# adding the defined resources along with their corresponding urls
api.add_resource(Welcome, '/')
api.add_resource(FloorMap, '/floors/<string:code>')
api.add_resource(FloorMapFile, '/floorplan/<string:code>')
api.add_resource(Graph, '/shortestpath')
api.add_resource(Event, '/events')
# driver function
if __name__ == '__main__':
    app.run(debug = True)
    conn.close()
