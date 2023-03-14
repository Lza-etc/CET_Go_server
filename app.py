from flask import Flask, jsonify, request, send_file
from flask_restful import Resource, Api
# from PIL import Image

# requires neo4j module to run query directly from this script
from neo4j import GraphDatabase

resources = {
    "floorMaps": {
        "CE": ['https://github.com/HariSK20/CETGo_Data/raw/main/CE0.png', 'https://github.com/HariSK20/CETGo_Data/raw/main/CE1.png', ], 
        "CSE": ['https://github.com/HariSK20/CETGo_Data/raw/main/cs0.svg', 'https://raw.githubusercontent.com/HariSK20/CETGo_Data/main/cs1.svg', 'https://github.com/HariSK20/CETGo_Data/raw/main/cs2.svg'],
        "MCA": ['none exists!']
    }
}

uri_to_server=""
usr = ""
pwd = ""

# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)
# making a class for a particular resource
# the get, post methods correspond to get and post requests
# they are automatically mapped by flask_restful.
# other methods include put, delete, etc.
class Welcome(Resource):
    def get(self):
        return(jsonify({'message': 'HELLO!!'}))


class FloorMap(Resource):
    # corresponds to the GET request.
    # this function is called whenever there
    # is a GET request for this resource
    def get(self, code):
        return jsonify({'src': resources['floorMaps'][code[:-1].upper()][int(code[-1])]})
    # Corresponds to POST request
    def post(self):
        data = request.get_json()     # status code
        return jsonify({'data': data}), 201


class FloorMapFile(Resource):
    def get(self, code):
        path = '../CETGo_Data/'+ code + '.svg'
        return send_file(path, mimetype='image/svg+xml')


class Graph(Resource):
    def get(self):
        data = request.args.to_dict()
        print(data)
        if(data == None):
            return(jsonify({'message': 'No data found'}))
        graphDB_Driver  = GraphDatabase.driver(uri_to_server, auth=(usr, pwd))
        with graphDB_Driver.session() as graphDB_Session:
            # checking if the nodes where returned correctly
            query = "match (p1:room {id: '{0}'}), (p2:room {id: '{1}'}), path = shortestPath((p1)-[*..15]-(p2)) return path".format(data['src'], data['dest'])
            res = graphDB_Session.run(query)
            print(res)
        graphDB_Driver.close()
        return(jsonify({'res': 'hello'}))


# adding the defined resources along with their corresponding urls
api.add_resource(Welcome, '/')
api.add_resource(FloorMap, '/floors/<string:code>')
api.add_resource(FloorMapFile, '/floorplan/<string:code>')
api.add_resource(Graph, '/shortestpath')

# driver function
if __name__ == '__main__':
    app.run(debug = True)
