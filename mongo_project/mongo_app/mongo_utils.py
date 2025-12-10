from pymongo import MongoClient
import gridfs

def get_mongo_connection(uri, dbname):
    client = MongoClient(uri)
    db = client[dbname]
    fs = gridfs.GridFS(db)
    return db, fs
