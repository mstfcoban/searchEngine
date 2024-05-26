from googleSettings import *
import requests
from urllib.parse import quote_plus, urlparse
from extractKeyWords import extractKeyWords
from database import visited_collection

def search_api(query, pages=int(RESULT_COUNT/10)):
    for i in range(0, pages):
        start = i*10+1
        url = SEARCH_URL.format(
            key=SEARCH_KEY,
            cx=SEARCH_ID,
            query=quote_plus(query),
            start=start
        )
        response = requests.get(url)
        data = response.json()

        try:
            for i in data["items"]:
                keywords_url = extractKeyWords(i['link'], True)
                keywords_title = extractKeyWords(i['title'])
                keywords_description = extractKeyWords(i['snippet'])

                title_keywords = [i[0] for i in keywords_title]
                title_value = [i[1] for i in keywords_title]
                description_keywords = [i[0] for i in keywords_description]
                description_value = [i[1] for i in keywords_description]

                keywords = {
                    'url': keywords_url,
                    'title': [x.lower() for x in title_keywords],
                    'title_value': title_value,
                    'description': [x.lower() for x in description_keywords],
                    'description_value': description_value,
                }

                data = {
                    'url': i['link'],
                    'domain': urlparse(i['link']).netloc,
                    'path': urlparse(i['link']).path,
                    'title': i['title'],
                    'description': i['snippet'],
                    'image': [i['pagemap']['organization'][0]['logo']] if i['pagemap'] and 'organization' in i['pagemap'].keys() and 'logo' in i['pagemap']['organization'][0].keys() else [],
                    'parent': 'google_api',
                    'level': 0,
                    'isCrawled': 0,
                    'keywords': keywords
                }

                insertDB(data)
        except:
            print('limit')

def insertDB(data):
    try:
        visited_collection.insert_one(data)
    except:
        query = {"url": data["url"]}
        data.pop('_id', None)
        newdata = {"$set": data}
        visited_collection.update_one(query, newdata)