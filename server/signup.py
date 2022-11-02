import re

from pymongo import MongoClient
from setup import *


def checkAccountExit(username):
    global data

    for user in data:
        user['username'] = str(user['username'])

        if user['username'] == username:
            return True

    return False


def checkAccountRequirement(username, password):
    if checkAccountExit(username):
        return -1

    if len(password) < 3 or len(username) < 5:
        return -2

    pattern = re.compile("[A-Za-z0-9]+")

    if pattern.fullmatch(username):
        return True

    return -2


def addUser(fullname, username, password):
    count = 0
    for x in data:
        count = x["_id"] + 1

    account = {"_id": count, "username": username,
               "password": password, "name": fullname}
    collection.insert_one(account)
    re_init_data()


def register(fullname,  username, password):
    if checkAccountRequirement(username, password) == -1:
        return "user name is exited"
    elif checkAccountRequirement(username, password) == -2:
        return "username or password is not qualified"
    else:
        addUser(fullname, username, password)
        return "Signed up successfully"
