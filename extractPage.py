from database import seed_collection, visited_collection
from extractKeyWords import extractKeyWords
from urllib.parse import urlparse
visited_url = set()

class ExtraxtPage():

    def __init__(self, response):
        self.response = response

    def process(self, is_seed):
        isCrawled = 0

        if self.response.status == 200:
            isCrawled = 1

        keywords_url = extractKeyWords(self.response.url, True)
        keywords_title = extractKeyWords(self.response.css('title::text').get())
        keywords_description = extractKeyWords(self.response.css('meta[name=description]::attr(content)').get())

        title_keywords = [i[0] for i in keywords_title]
        title_value = [i[1] for i in keywords_title]
        description_keywords = [i[0] for i in keywords_description]
        description_value = [i[1] for i in keywords_description]

        url = self.response.url or ''
        domain = urlparse(self.response.url).netloc or ''
        path = urlparse(self.response.url).path or ''
        title = self.response.css('title::text').get() if self.response.css('title::text').get() else ''
        description = self.response.css('meta[name=description]::attr(content)').get() if self.response.css('meta[name=description]::attr(content)').get() else ''
        parent = self.response.request.headers.get('Referer', None).decode() if self.response.request.headers.get('Referer', None) else ''
        level = self.response.request.meta.get('depth')
        keywords = {
            'url': keywords_url,
            'title': [x.lower() for x in title_keywords],
            'title_value': title_value,
            'description': [x.lower() for x in description_keywords],
            'description_value': description_value,
        }
        imagedata = []

        for image in self.response.css('img'):
            imagedata.append({
                'url': self.response.urljoin(image.attrib['src']) if 'src' in image.attrib.keys() else '',
                'title': image.attrib.get('alt', '')
            })

        data = {
            'url': url,
            'domain': domain,
            'path': path,
            'title': title,
            'description': description,
            'image': imagedata,
            'parent': parent,
            'level': level,
            'isCrawled': isCrawled,
            'keywords': keywords
        }

        try:
            if is_seed:
                seed_collection.insert_one(data)
            else:
                visited_collection.insert_one(data)
        except:
            query = {"url": url}
            data.pop('_id', None)
            newdata = {"$set": data}
            visited_collection.update_one(query, newdata)