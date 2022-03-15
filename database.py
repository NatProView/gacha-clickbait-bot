def get_database():
    from pymongo import MongoClient

    credentials_file = open("mongodb-credentials", 'r')
    connection_string = credentials_file.read()
    credentials_file.close()

    client = MongoClient(connection_string)

    return client['gacha-bot']


if __name__ == "__main__":
    dbname = get_database()
    collection_name = dbname["User"]