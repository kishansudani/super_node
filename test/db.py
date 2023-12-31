import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["mycollection"]

# Define a sample document with an array
document = {
    "name": "John Doe",
    "favorite_colors": ["blue", "green", "red"]
}

# Insert the document into the collection
collection.insert_one(document)

# Append data to the array
new_color = "yellow"
collection.update_one(
    {"name": "John Doe"},
    {"$push": {"favorite_colors": new_color}}
)

# Delete data from the array
color_to_remove = "red"
collection.update_one(
    {"name": "John Doe"},
    {"$pull": {"favorite_colors": color_to_remove}}
)




# db.reward.find({node: "127.0.0.1:ANC"}, {"_id": 1})
# db.reward.updateOne({node: "127.0.0.1:ANC"},{$inc: {"amount": 10}})
# db.reward.insertOne({node: "127.0.0.1:ANC", amount: 10})
