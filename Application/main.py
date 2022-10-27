from typing import Text
from unittest import result
from urllib import response
from flask import *
import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TEXT, Identity, inspect, select, update
from sqlalchemy_utils import database_exists, create_database
import boto3
from botocore.exceptions import ClientError
import json
import uuid
import os

app = Flask(__name__)

with open('/etc/environment.json') as config_file:
  config = json.load(config_file)

engine=create_engine('postgresql://'+str(config.get('DB_USER_NAME'))+':'+str(config.get('DB_PASSWORD'))+'@'+str(config.get('DB_ADDRESS'))+':5432/'+str(config.get('DB_NAME')))
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

Upload_Details = Table(
'Upload_Details',meta,
Column('id',Integer,Identity(start=1),primary_key=True),
Column('user_id',Integer),
Column('doc_id',String),
Column('filename',String),
Column('date_created',String),
Column('s3_bucket_path',String),
)

meta_data = Table(
'meta_data', meta,
Column('id',Integer,Identity(start=1),primary_key=True),
Column('user_id',Integer),
Column('S3_metadata',String),
)

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

@app.route('/v1/documents/<accountId>', methods=['POST'])
def documentUpload(accountId):
    bcrypt = Bcrypt(app)
    queryStatement = User_Details.select().where(User_Details.c.id==accountId)
    conn = engine.connect()
    result = conn.execute(queryStatement)
    account = result.fetchone()
    if(account==None):
        data = {'message':'There is no user with this account ID','code':'NOT FOUND'}
        return make_response(jsonify(data),400)
    else:
        password = account["password"][2:-1]
        if request.authorization and request.authorization.username==account["username"] and bcrypt.check_password_hash(password,request.authorization.password):
            uploaded_file = request.files.get('UploadedFile')
            if  uploaded_file.filename != '':
                uploaded_file.save(os.path.join('/home/ubuntu',uploaded_file.filename))
                s3_client = boto3.client('s3')
                object_id = str(uuid.uuid4())
                object_name=object_id+"/"+str(uploaded_file.filename)
                try:
                    s3_client.upload_file(os.path.join('/home/ubuntu',uploaded_file.filename),config.get('AWS_BUCKET_NAME'),object_name)
                    head_object = s3_client.head_object(Bucket=config.get('AWS_BUCKET_NAME'),Key=object_name)
                    conn = engine.connect()
                    result=conn.execute(Upload_Details.insert(),[{'user_id':accountId,'doc_id':object_id,'filename':str(uploaded_file.filename),'date_created':head_object['ResponseMetadata']['HTTPHeaders']['date'],'s3_bucket_path':"/home/ubuntu"+str(uploaded_file.filename)}])
                    result1=conn.execute(meta_data.insert(),[{'user_id':accountId,'S3_metadata':str(head_object)}])
                    #return_json = json.dumps(str(head_object),indent=4,sort_keys=True)
                    return_json = {'doc_id': object_id,'user_id':accountId,'name':str(uploaded_file.filename),'date_created':head_object['ResponseMetadata']['HTTPHeaders']['date'],'s3_bucket_path':"/home/ubuntu"+str(uploaded_file.filename)}
                    return make_response(return_json,201)
                except Exception as e:
                    # This is a catch all exception, edit this part to fit your needs.
                    print("Something Happened: ", e)
                    data = {'message': str(e), 'code': 'File error'}
                    return make_response(jsonify(data),400)
            else:
                data = {'message':'No file is uploaded','code':'File empty'}
                return make_response(jsonify(data), 400)
        else:
            if request.authorization:
                data = {'message':'Credentials is incorrect'}
                return make_response(jsonify(data),401)
            else:
                data = {'message':'Authorization info is not provided','code':"UNAUTHORIZED"}
                return make_response(jsonify(data), 401)

@app.route('/v1/documents/<accountId>', methods=['GET'])
def listDocuments(accountId):
    bcrypt = Bcrypt(app)
    queryStatement = User_Details.select().where(User_Details.c.id==accountId)
    conn = engine.connect()
    result = conn.execute(queryStatement)
    account = result.fetchone()
    if(account==None):
        data = {'message':'There is no user with this account ID','code':'NOT FOUND'}
        return make_response(jsonify(data),400)
    else:
        password = account["password"][2:-1]
        if request.authorization and request.authorization.username==account["username"] and bcrypt.check_password_hash(password,request.authorization.password):
            queryStatement1 = Upload_Details.select().where(Upload_Details.c.user_id==accountId)
            conn = engine.connect()
            result = conn.execute(queryStatement1)
            upload_list = result.fetchall()
            list1=[]
            for row in upload_list:
                a=0
                for x in row:
                    x=str(x)
                    if(a==1):
                        user_id1=x
                    if(a==2):
                        doc_id1=x
                    if(a==3):
                        filename1=x
                    if(a==4):
                        date_created1=x
                    if(a==5):
                        s3_bucket_path1=x
                    a=a+1
                row_json={"doc_id":doc_id1,"user_id":user_id1,"name":filename1,"date_created":date_created1,"s3_bucket_path":s3_bucket_path1}
                list1.append(row_json)
            return str(list1)
        else:
            if request.authorization:
                data = {'message':'Credentials is incorrect'}
                return make_response(jsonify(data),401)
            else:
                data = {'message':'Authorization info is not provided','code':"UNAUTHORIZED"}
                return make_response(jsonify(data), 401)

@app.route('/v1/documents/<accountId>/<doc_id>', methods=['GET'])
def getDocument(accountId,doc_id):
    bcrypt = Bcrypt(app)
    queryStatement = User_Details.select().where(User_Details.c.id==accountId)
    conn = engine.connect()
    result = conn.execute(queryStatement)
    account = result.fetchone()
    if(account==None):
        data = {'message':'There is no user with this account ID','code':'NOT FOUND'}
        return make_response(jsonify(data),400)
    else:
        password = account["password"][2:-1]
        if request.authorization and request.authorization.username==account["username"] and bcrypt.check_password_hash(password,request.authorization.password):
            queryStatement1 = Upload_Details.select().where(Upload_Details.c.user_id==accountId and Upload_Details.c.doc_id==doc_id)
            conn = engine.connect()
            result = conn.execute(queryStatement1)
            upload_list = result.fetchall()
            list1=[]
            for row in upload_list:
                a=0
                for x in row:
                    x=str(x)
                    if(a==1):
                        user_id1=x
                    if(a==2):
                        doc_id1=x
                    if(a==3):
                        filename1=x
                    if(a==4):
                        date_created1=x
                    if(a==5):
                        s3_bucket_path1=x
                    a=a+1
                if doc_id==doc_id1:
                    row_json={"doc_id":doc_id1,"user_id":user_id1,"name":filename1,"date_created":date_created1,"s3_bucket_path":s3_bucket_path1}
                    list1.append(row_json)
            return str(list1)
        else:
            if request.authorization:
                data = {'message':'Credentials is incorrect'}
                return make_response(jsonify(data),401)
            else:
                data = {'message':'Authorization info is not provided','code':"UNAUTHORIZED"}
                return make_response(jsonify(data), 401)

@app.route('/v1/documents/<accountId>/<documentId>', methods=['DELETE'])
def deleteDocuments(accountId,documentId):
    bcrypt = Bcrypt(app)
    queryStatement = User_Details.select().where(User_Details.c.id==accountId)
    conn = engine.connect()
    result = conn.execute(queryStatement)
    account = result.fetchone()
    if(account==None):
        data = {'message':'There is no user with this account ID','code':'NOT FOUND'}
        return make_response(jsonify(data),400)
    else:
        password = account["password"][2:-1]
        if request.authorization and request.authorization.username==account["username"] and bcrypt.check_password_hash(password,request.authorization.password):
            s3_client = boto3.client("s3")
            queryStatement1 = Upload_Details.select().where(Upload_Details.c.user_id==accountId)
            conn = engine.connect()
            result = conn.execute(queryStatement1)
            upload_list = result.fetchall()
            list1=[]
            for row in upload_list:
                a=0
                for x in row:
                    x=str(x)
                    if(a==1):
                        user_id1=x
                    if(a==2):
                        doc_id1=x
                    if(a==3):
                        filename1=x
                    if(a==4):
                        date_created1=x
                    if(a==5):
                        s3_bucket_path1=x
                    a=a+1
                if documentId==doc_id1:
                    row_json={"doc_id":doc_id1,"user_id":user_id1,"name":filename1,"date_created":date_created1,"s3_bucket_path":s3_bucket_path1}
                    list1.append(row_json)
            if len(list1)==0:
                data={"message":"There is no document with this document id for this user"}
                return make_response(jsonify(data),404)
            else:
                response = s3_client.delete_object(Bucket=config.get('AWS_BUCKET_NAME'),Key=(row_json["doc_id"]+"/"+row_json["name"]))
                queryStatement2 = Upload_Details.delete().where(Upload_Details.c.doc_id==documentId)
                conn = engine.connect()
                result = conn.execute(queryStatement2)
                data={"message":"Bucket Deleted successfully"}
                return make_response(jsonify(data),204)
        else:
            if request.authorization:
                data = {'message':'Credentials is incorrect'}
                return make_response(jsonify(data),401)
            else:
                data = {'message':'Authorization info is not provided','code':"UNAUTHORIZED"}
                return make_response(jsonify(data), 401)

@app.route('/v1/account', methods=['POST'])
def home_page():
    bcrypt = Bcrypt(app)
    if "first_name" not in request.json or "last_name" not in request.json or "password" not in request.json or "username" not in request.json:
        data = {'message': 'Enter all the required details for user creation in the request json', 'code': 'BAD REQUEST'}
        return make_response(jsonify(data), 400)
    else:
        try:
            firstname = request.json["first_name"]
            last_name = request.json["last_name"]
            password = str(bcrypt.generate_password_hash(request.json["password"]))
            username = request.json["username"]
            account_created = str(datetime.datetime.now())
            account_updated = str(datetime.datetime.now())
            
            conn = engine.connect()
            result=conn.execute(User_Details.insert(),[{'first_name':firstname,'last_name':last_name,'username':username,'password':password,'account_created':account_created,'account_updated':account_updated}])
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
                data = {'message': 'Authorization info is incorrect','code':"FORBIDDEN"}
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
        