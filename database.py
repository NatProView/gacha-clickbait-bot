def get_database():
    from pymongo import MongoClient
    import pymongo

    credentials_file = open("mongodb-credentials", 'r')
    CONNECTION_STRING = credentials_file.read()
    credentials_file.close()

    client = MongoClient(CONNECTION_STRING)

    return client['gacha-bot']

if __name__ == "__main__":
    dbname = get_database();
    collection_name = dbname["User"]

collection_name.insert_one({"_id": "140237130549952513", "name": "Nicofisi"})