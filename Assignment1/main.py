from urllib import response
from flask import *
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt

app = Flask(__name__)

def getFromDB(queryString,id):
    try:
        conn = psycopg2.connect(database="CSYE_6225", user='postgres', password='ece18670!', host='localhost', port= '5433')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(queryString,(id,))
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result
    except:
        print("Exception in getFromDB function for query: "+queryString+" id: "+ str(id))
        return [{"Message":"Exception in getFromDB function for query: "+queryString+" id: "+ str(id)}]

def putInDB(queryString):
    try:
        conn = psycopg2.connect(database="CSYE_6225", user='postgres', password='ece18670!', host='localhost', port= '5433')
        cursor = conn.cursor()
        cursor.execute(queryString)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        print("Exception in putInDB function for query: "+queryString)
        return [{"Message":"Exception in putInDB function for query: "+queryString}]

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
            queryString = "INSERT INTO public.\"User_Details\"(\"first_name\",\"last_name\",\"Password1\",\"username\",\"account_created\",\"account_updated\") VALUES (%s,%s,%s,%s,%s,%s);"

            conn = psycopg2.connect(database="CSYE_6225", user='postgres', password='ece18670!', host='localhost', port= '5433')
            cursor = conn.cursor()
            cursor.execute(queryString,(first_name,last_name,password,username,account_created,account_updated,))
            conn.commit()
            conn.close()
        except:
            data = {'message': 'Error occured while inserting in DB', 'code': 'DB Error'}
            return make_response(jsonify(data), 400)

    data = {'message': 'New user account successfully created', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)

@app.route('/v1/account/<accountId>', methods=['GET'])
def view_page(accountId):
    bcrypt = Bcrypt(app)
    queryStatement = "SELECT * FROM public.\"User_Details\" WHERE \"User_Details\".\"id\"=%s;"
    account = getFromDB(queryStatement,accountId)
    if(len(account)==0):
        data = {'message': 'There is no user with this account ID', 'code': 'NOT FOUND'}
        return make_response(jsonify(data), 400)
    else:
        account[0]["Password1"] = account[0]["Password1"][2:-1]
        if request.authorization and request.authorization.username==account[0]["username"] and bcrypt.check_password_hash(account[0]["Password1"],request.authorization.password):
            data = {"id": accountId, "first_name": account[0]["first_name"], "last_name": account[0]["last_name"], "username": account[0]["username"], "account_created": account[0]["account_created"], "account_updated": account[0]["account_updated"]}
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
    queryStatement = "SELECT * FROM public.\"User_Details\" WHERE \"User_Details\".\"id\"=%s;"
    account = getFromDB(queryStatement,accountId)
    if(len(account)==0):
        data = {'message': 'There is no user with this account ID', 'code': 'NOT FOUND'}
        return make_response(jsonify(data), 400)
    else:
        account[0]["Password1"] = account[0]["Password1"][2:-1]
        if request.authorization and request.authorization.username==account[0]["username"] and bcrypt.check_password_hash(account[0]["Password1"],request.authorization.password):
            if "first_name" not in request.json and "last_name" not in request.json and "username" not in request.json and "password" not in request.json:
               data = {'message': 'There is no detail provided to update the user', 'code': 'BAD REQUEST'}
               return make_response(jsonify(data), 400)
            if "first_name" in request.json:
                first_name = request.json["first_name"]
                account_updated = str(datetime.datetime.now())
                queryString = "UPDATE public.\"User_Details\" SET \"first_name\"='" + first_name + "', \"account_updated\"='"+ account_updated + "'WHERE \"id\"='"+ str(accountId) +"';"
                putInDB(queryString)
            if "last_name" in request.json:
                last_name = request.json["last_name"]
                account_updated = str(datetime.datetime.now())
                queryString = "UPDATE public.\"User_Details\" SET \"last_name\"='" + last_name + "', \"account_updated\"='"+ account_updated + "' WHERE \"id\"='"+ str(accountId) +"';"
                putInDB(queryString)
            if "username" in request.json:
                username = request.json["username"]
                account_updated = str(datetime.datetime.now())
                queryString = "UPDATE public.\"User_Details\" SET \"username\"='" + username + "', \"account_updated\"='"+ account_updated + "' WHERE \"id\"='"+ str(accountId) +"';"
                putInDB(queryString)
            if "password" in request.json:
                password=str(bcrypt.generate_password_hash(request.json["password"]))
                account_updated = str(datetime.datetime.now())
                queryString = "UPDATE public.\"User_Details\" SET \"Password1\"=%s, \"account_updated\"=%s WHERE \"id\"='"+ str(accountId) +"';"
                conn = psycopg2.connect(database="CSYE_6225", user='postgres', password='ece18670!', host='localhost', port= '5433')
                cursor = conn.cursor()
                cursor.execute(queryString,(password,account_updated,))
                conn.commit()
                conn.close()

            data = {'message': 'The given details are successfully updated', 'code': 'SUCCESS'}
            return make_response(jsonify(data), 204)
        else:
            if request.authorization:
                data = {'message': 'Authorization info is incorrect','code':	"FORBIDDEN"}
                return make_response(jsonify(data), 403)
            else:
                data = {'message': 'Authorization info is not provided','code':	"UNAUTHORIZED"}
                return make_response(jsonify(data), 401)


if __name__ == '__main__':
    app.run(port=8080)