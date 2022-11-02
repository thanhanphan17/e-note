from setup import *
from pymongo import MongoClient


def authenticate(username, password):
    global data
    for user in data:
        if user['username'] == username and user['password'] == password:
            return user

    return False


def loginMessage(username, password):
    if authenticate(username, password):
        return "Login successfully!"
    else:
        return "Login fail, try to uy new account!"
