from flask import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home_page():
    data = {'message': 'Done', 'code': 'SUCCESS'}

    return make_response(jsonify(data), 200)


if __name__ == '__main__':
    app.run(port=8080)