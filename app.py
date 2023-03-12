from flask import Flask, jsonify, request
from flask_restful import Resource, Api

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

# another resource to calculate the square of a number
# class Square(Resource):
#     def get(self, num):
#         return jsonify({'square': num**2})
  
# adding the defined resources along with their corresponding urls
api.add_resource(Welcome, '/')
  
  
# driver function
if __name__ == '__main__':
    app.run(debug = True)
