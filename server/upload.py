from pymongo import MongoClient
from PIL import Image

cluster = MongoClient(
    "mongodb+srv://thanhanphan17:05062003@cluster0.dwxs1.mongodb.net/?retryWrites=true&w=majority")
db = cluster["e-note"]
clt = db["note"]


def note_size():
    data = clt.find()
    count = 0
    for x in data:
        count += 1

    return count


def add_note(note):
    global clt
    data = clt.find()
    count = 0
    for x in data:
        count += 1
    note["_id"] = count
    clt.insert_one(note)
