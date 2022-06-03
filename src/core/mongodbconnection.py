from pymongo import MongoClient


class MongoDBConnection:
    # "mongodb+srv://admin:taxiadmin123@cluster0.2p1ix.mongodb.net/?retryWrites=true&w=majority"
    def __init__(self, mongo_uri, database_name):
        self.connection = None
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.database = None

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    def __enter__(self):
        self.connection = MongoClient(self.mongo_uri)
        self.database = self.connection[self.database_name]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
