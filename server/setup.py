from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://thanhanphan17:05062003@cluster0.dwxs1.mongodb.net/?retryWrites=true&w=majority")
db = cluster["e-note"]
collection = db["user"]
dataObject = collection.find()

data = []
for user in dataObject:
    user['username'] = str(user['username'])
    user['password'] = str(user['password'])
    data.append(user)


def re_init_data():
    dataObject = collection.find()
    data.clear()

    for user in dataObject:
        user['username'] = str(user['username'])
        user['password'] = str(user['password'])
        data.append(user)
