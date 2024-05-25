import pymongo

#connected db
client = pymongo.MongoClient('mongodb://localhost:27017/')
#client.drop_database('crawl')
db = client['crawl']

seed_collection = db['seed_urls']
seed_collection.create_index('url', unique=True)

visited_collection = db['visited_urls']
visited_collection.create_index('url', unique=True)