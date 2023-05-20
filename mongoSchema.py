from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from collections import OrderedDict


db = MongoClient("mongodb://localhost:27017/")['bookstoredb']
