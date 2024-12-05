from pymongo import MongoClient

uri = "mongodb+srv://ikedinachimugochukwu:kVE8MslMtMYRZqbt@cs531cluster.gxaub.mongodb.net/?retryWrites=true&w=majority&appName=CS531Cluster"
client = MongoClient(uri)
try:
    database = client.get_database("finances")
    database.create_collection("expenses")
    database.create_collection("income")
    database.create_collection("goals")
    print(database)
    client.close()
except Exception as e:
    raise Exception("Unable to find the document due to the following error: ", e)

