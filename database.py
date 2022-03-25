def get_database():
    from pymongo import MongoClient
    import os

    client = MongoClient(os.environ.get('MONGODB_CONNECTION_STRING'))

    return client['gacha-bot']


if __name__ == "__main__":
    dbname = get_database()
    collection_name = dbname["User"]