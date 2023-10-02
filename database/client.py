from pymongo import MongoClient

def new_client(collection):
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['CLUSTER']
        collection = db[collection]
    except:
        print(f'{collection} DATABASE connection error')
    
    return collection