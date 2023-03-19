from flask import Flask, jsonify, request, send_file
from flask_restful import Resource, Api
from dotenv import dotenv_values
# from PIL import Image
# requires neo4j module to run query directly from this script
from neo4j import GraphDatabase
import psycopg2 as psql
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

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

# 
login_manager = LoginManager()
# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)
app.config['SECRET_KEY'] = 'mysecretkey'
login_manager.init_app(app)

conn = psql.connect(dbname=psql_db, user=psql_usr, password=psql_pass, host=psql_host, port=psql_port)
        
class Welcome(Resource):
    """ 
        Class for root page
    """
    def get(self):
        return(jsonify({'message': 'HELLO!!'}))


class FloorMap(Resource):
    """
        Class for getting details of floors of a building
    """
    def get(self, code):
        global conn
        res = {'src': resources['floorMaps'][code[:-1].upper()][int(code[-1])]}
        cur = conn.cursor()
        res['rooms'] = []
        cur.execute("SELECT id,val FROM {} where z='{}'".format("cse", code[-1]))
        for i in cur.fetchall():
            res['rooms'].append({'ID': i[0], 'Description': i[1]})
        cur.close()
        return jsonify(res)
    # Corresponds to POST request
    def post(self):
        data = request.get_json()     # status code
        return jsonify({'data': data}), 201


class FloorMapFile(Resource):
    """ 
        Class for getting floor map file of each department
    """
    def get(self, code):
        path = '../CETGo_Data/'+ code + '.svg'
        return send_file(path, mimetype='image/svg+xml')


class Graph(Resource):
    """ 
        Class for getting shortest path data from Neo4J
    """
    def get(self):
        data = request.args.to_dict()
        print(data)
        if(data == None):
            return(jsonify({'message': 'No data found'}))
        graphDB_Driver  = GraphDatabase.driver(neo4j_uri_to_server, auth=(neo4j_usr, neo4j_pwd))
        with graphDB_Driver.session() as graphDB_Session:
            # checking if the nodes where returned correctly
            query = "match (p1:room {id: '{0}'}), (p2:room {id: '{1}'}), path = shortestPath((p1)-[*..15]-(p2)) return path".format(data['src'], data['dest'])
            res = graphDB_Session.run(query)
            print(res)
        graphDB_Driver.close()
        return(jsonify({'res': 'hello'}))


class User(UserMixin):
    """ 
        User class for login
    """
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        # self.email = email

    @staticmethod
    def get_by_username(username):
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
            if row is not None:
                return User(id=row[0], username=row[1], password=row[2])
            else:
                return None

    @staticmethod
    def get_by_id(id):
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (id,))
            row = cur.fetchone()
            if row is not None:
                return User(id=row[0], username=row[1], password=row[2])
            else:
                return None

    def to_json(self):        
        return {"name": self.username}
                # "email": self.email}

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = User.get_by_username(username)
        if user is not None and user.password == password:
            login_user(user)
            return {'message': 'Login successful.'}
        else:
            return {'message': 'Invalid username or password.'}


class Protected(Resource):
    @login_required
    def get(self):
        return {'message': f'Hello, {current_user.username}!'}


class Logout(Resource):
    @login_required
    def post(self):
        logout_user()
        return {'message': 'Logout successful.'}


# adding the defined resources along with their corresponding urls
api.add_resource(Welcome, '/')
api.add_resource(FloorMap, '/floors/<string:code>')
api.add_resource(FloorMapFile, '/floorplan/<string:code>')
api.add_resource(Graph, '/shortestpath')
api.add_resource(Login, '/login')
api.add_resource(Protected, '/protected')
api.add_resource(Logout, '/logout')
# driver function
if __name__ == '__main__':
    app.run(debug = True)
    conn.close()
