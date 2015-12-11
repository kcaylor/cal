from pymongo import MongoClient

DATABASE = 'arable'

client = MongoClient()
db = client[DATABASE]
