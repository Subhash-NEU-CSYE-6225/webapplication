from typing import Text
from unittest import result
from urllib import response
from flask import *
import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TEXT, Identity, inspect, select, update
from sqlalchemy_utils import database_exists, create_database

DB_Name='csye6225'
engine=create_engine('postgresql://postgres:ece18670!@localhost/'+str(DB_Name))
if not database_exists(engine.url):
    create_database(engine.url)

meta = MetaData()

User_Details = Table(
'User_Details',meta,
Column('id',Integer,Identity(start=1),primary_key=True),
Column('first_name',String),
Column('last_name',String),
Column('username',String,unique=True),
Column('password',TEXT),
Column('account_created',String),
Column('account_updated',String),
)

app = Flask(__name__)

with app.app_context():
    meta.create_all(engine)
    for a in meta.tables:
        new_column_list = []
        s = "select * from public.\""+ str(a) +"\";"
        conn = engine.connect()
        result = conn.execute(s)
        row = result.fetchone()
        if row!=None:
            for x in meta.tables[a].columns:
                new_column = str(x).replace(str(a)+".","")
                new_column_list.append(new_column)
                if(new_column not in row.keys()):
                    table_name = str(a)
                    column_name = str(new_column)
                    column_type = str(x.type)
                    query = 'ALTER TABLE public.\"'+table_name+'\" ADD \"'+column_name+'\" '+column_type+';'
                    conn.execute(query)
        else:
            qs="DROP TABLE public.\""+ str(a) +"\";"
            conn.execute(qs)
            meta.create_all(engine)

@app.route('/healthz', methods=['GET'])
def healthz():
    data = {'message': 'OK', 'code': '200'}
    return make_response(jsonify(data), 200)

@app.route('/v1/account', methods=['POST'])
def home_page():
    bcrypt = Bcrypt(app)
    if "first_name" not in request.json or "last_name" not in request.json or "password" not in request.json or "username" not in request.json:
        data = {'message': 'Enter all the required details for user creation in the request json', 'code': 'BAD REQUEST'}
        return make_response(jsonify(data), 400)
    else:
        try:
            first_name = request.json["first_name"]
            last_name = request.json["last_name"]
            password = str(bcrypt.generate_password_hash(request.json["password"]))
            username = request.json["username"]
            account_created = str(datetime.datetime.now())
            account_updated = str(datetime.datetime.now())
            
            conn = engine.connect()
            result=conn.execute(User_Details.insert(),[{'first_name':first_name,'last_name':last_name,'username':username,'password':password,'account_created':account_created,'account_updated':account_updated}])
        except:
            data = {'message': 'Error occured while inserting in DB or the username already exits', 'code': 'DB Error'}
            return make_response(jsonify(data), 400)

    queryStatement = User_Details.select().where(User_Details.c.username==username)
    conn = engine.connect()
    result = conn.execute(queryStatement)
    account = result.fetchone()
    if account==None:
        data = {'message': 'Error occured while inserting in DB or the username already exits', 'code': 'DB Error'}
        return make_response(jsonify(data), 400)
    else:
        data = {"id": account["id"], "first_name": account["first_name"], "last_name": account["last_name"], "username": account["username"], "account_created": account["account_created"], "account_updated": account["account_updated"]}
        return make_response(jsonify(data), 201)

@app.route('/v1/account/<accountId>', methods=['GET'])
def view_page(accountId):
    bcrypt = Bcrypt(app)
    queryStatement = User_Details.select().where(User_Details.c.id==accountId)
    conn = engine.connect()
    result = conn.execute(queryStatement)
    account = result.fetchone()
    if(account==None):
        data = {'message': 'There is no user with this account ID', 'code': 'NOT FOUND'}
        return make_response(jsonify(data), 400)
    else:
        password = account["password"][2:-1]
        if request.authorization and request.authorization.username==account["username"] and bcrypt.check_password_hash(password,request.authorization.password):
            data = {"id": accountId, "first_name": account["first_name"], "last_name": account["last_name"], "username": account["username"], "account_created": account["account_created"], "account_updated": account["account_updated"]}
            return make_response(jsonify(data), 200)
        else:
            if request.authorization:
                data = {'message': 'Authorization info is incorrect','code':	"FORBIDDEN"}
                return make_response(jsonify(data), 403)
            else:
                data = {'message': 'Authorization info is not provided','code':	"UNAUTHORIZED"}
                return make_response(jsonify(data), 401)


@app.route('/v1/account/<accountId>', methods=['PUT'])
def update_page(accountId):
    bcrypt = Bcrypt(app)
    queryStatement = User_Details.select().where(User_Details.c.id==accountId)
    conn = engine.connect()
    result = conn.execute(queryStatement)
    account = result.fetchone()
    if(account==None):
        data = {'message': 'There is no user with this account ID', 'code': 'NOT FOUND'}
        return make_response(jsonify(data), 400)
    else:
        password = account["password"][2:-1]
        if request.authorization and request.authorization.username==account["username"] and bcrypt.check_password_hash(password,request.authorization.password):
            if "first_name" not in request.json and "last_name" not in request.json and "username" not in request.json and "password" not in request.json:
               data = {'message': 'There is no detail provided to update the user', 'code': 'BAD REQUEST'}
               return make_response(jsonify(data), 400)
            if "first_name" in request.json:
                first_name = request.json["first_name"]
                account_updated = str(datetime.datetime.now())
                queryString = "UPDATE public.\"User_Details\" SET \"first_name\"='" + first_name + "', \"account_updated\"='"+ account_updated + "'WHERE \"id\"='"+ str(accountId) +"';"
                conn.execute(queryString)
            if "last_name" in request.json:
                last_name = request.json["last_name"]
                account_updated = str(datetime.datetime.now())
                queryString = "UPDATE public.\"User_Details\" SET \"last_name\"='" + last_name + "', \"account_updated\"='"+ account_updated + "' WHERE \"id\"='"+ str(accountId) +"';"
                conn.execute(queryString)
            if "username" in request.json:
                username = request.json["username"]
                account_updated = str(datetime.datetime.now())
                queryString = "UPDATE public.\"User_Details\" SET \"username\"='" + username + "', \"account_updated\"='"+ account_updated + "' WHERE \"id\"='"+ str(accountId) +"';"
                conn.execute(queryString)
            if "password" in request.json:
                newpassword=str(bcrypt.generate_password_hash(request.json["password"]))
                account_updated = str(datetime.datetime.now())
                u = update(User_Details)
                u = u.values({"password": newpassword,"account_updated":account_updated})
                u = u.where(User_Details.c.id == accountId)
                engine.execute(u)
            
            data = {'first_name': first_name}
            return make_response(jsonify(data), 204)
        else:
            if request.authorization:
                data = {'message': 'Authorization info is incorrect','code':	"FORBIDDEN"}
                return make_response(jsonify(data), 403)
            else:
                data = {'message': 'Authorization info is not provided','code':	"UNAUTHORIZED"}
                return make_response(jsonify(data), 401)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
        