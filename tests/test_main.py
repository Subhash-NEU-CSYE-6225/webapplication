import requests

def test_home_page():
    url = "http://127.0.0.1:8080/v1/account"
    myobj1 = {"first_name": "Jane",
              "last_name": "Doe",
              "password": "somepassword",
              "username": "jane.doe@example.com"}

    myobj2 = {"first_name": "Jane",
              "last_name": "Doe",
              "password": "somepassword"}

    result1 = requests.post(url,json=myobj1)

    result2 = requests.post(url,json=myobj2)

    assert result2.status_code==400
