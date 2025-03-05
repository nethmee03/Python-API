from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)
api = Api(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"

user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, help='Name cannot be blank', required=True)
user_args.add_argument('email', type=str, help='Email cannot be blank', required=True)

patch_args = reqparse.RequestParser()
patch_args.add_argument('name', type=str, required=False)
patch_args.add_argument('email', type=str, required=False)

userFields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = User.query.all()
        return users

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = User.query.filter_by(email=args['email']).first()
        if user:
            abort(400, message="User with this email already exists")

        new_user = User(name=args['name'], email=args['email'])
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201

class UserResource(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = User.query.get(id)
        if not user:
            abort(404, message='User not found')
        return user

    @marshal_with(userFields)
    def put(self, id):
        args = user_args.parse_args()
        user = User.query.get(id)
        if not user:
            abort(404, message='User not found')
        
        user.name = args['name']
        user.email = args['email']
        db.session.commit()
        return user, 200

    @marshal_with(userFields)
    def patch(self, id):
        args = patch_args.parse_args()
        user = User.query.get(id)
        if not user:
            abort(404, message='User not found')

        if args['name']:
            user.name = args['name']
        if args['email']:
            user.email = args['email']

        db.session.commit()
        return user, 200

    def delete(self, id):
        user = User.query.get(id)
        if not user:
            abort(404, message='User not found')
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 204
    
api.add_resource(Users, '/api/users')
api.add_resource(UserResource, '/api/user/<int:id>')

@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized successfully")

    print("Starting Flask app...")
    app.run(debug=True)


