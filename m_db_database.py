from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
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

