from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from analysisPage import setWord, removeStopWords, lemmatization, calculateScore, calculateTFIDF, rankeAlgo, Ner
import asyncio
from googleSearch import *

from database import visited_collection
import wordsegment
wordsegment.load()

@csrf_exempt
def home(request):
    template = loader.get_template('index.html')

    context = {}

    return HttpResponse(template.render(context, request))

def result(request):
    template = loader.get_template('result.html')
    sorted_data = []
    final_data = []
    word = request.GET.get('search', None)

    tfidf_dict = {
        'url': [],
        'title': [],
        'description': [],
    }

    ranke_dict = {
        'url': [],
        'title': [],
        'description': [],
    }

    if word:
        word = word.lower()

        #search with google api
        search_api(word)

        data = visited_collection.aggregate([{
            "$match": {
                "$or": [
                    {"keywords.url": {"$regex": word.replace(' ', '|'), "$options": "i"}},
                    {"keywords.title": {"$regex": word, "$options": "i"}},
                    # {"keywords.title": {"$regex": word.replace(' ', '|'), "$options": "i"}},
                    {'keywords.description': {"$regex": word, "$options": "i"}},
                    # {'keywords.description': {"$regex": word.replace(' ', '|'), "$options": "i"}},
                ],
                "title": {"$ne": None},
                "description": {"$ne": None},
            }
        }])

        results = list(data)

        for index, i in enumerate(results):
            setWord(word)

            tfidf_dict['url'].append(i['url'])
            tfidf_dict['title'].append(i['title'])
            tfidf_dict['description'].append(i['description'])

            ranke_dict['url'].append(i['keywords']['url'])
            ranke_dict['title'].append(i['keywords']['title'])
            ranke_dict['description'].append(i['keywords']['description'])

            filtered_data = removeStopWords(i)
            i['title_without_stop_words'] = filtered_data[0]
            i['description_without_stop_words'] = filtered_data[1]

            lemmatized = lemmatization(i)
            i['title_lemmatized'] = lemmatized[0]
            i['description_lemmatized'] = lemmatized[1]

            # score = calculateScore(word, i)

            # i['score'] = score

        similarities_tfidf = calculateTFIDF(word, tfidf_dict)

        similarities_rank = rankeAlgo(word, ranke_dict)

        for index, i in enumerate(results):
            score_tfidf = similarities_tfidf['url'][index] + similarities_tfidf['title'][index] + \
                          similarities_tfidf['description'][index]
            score_rank = similarities_rank['url'][index] + similarities_rank['title'][index] + \
                         similarities_rank['description'][index]

            i['score'] = score_tfidf + score_rank

        sorted_data = sorted(results, key=lambda x: x['score'], reverse=True)
        final_data = []
        for d in sorted_data:
            decision = Ner(d)
            if d['score'] > 0.5 and decision['isCompany']:
                final_data.append(d)

    context = {
        'data': final_data,
        'word': word
    }

    return HttpResponse(template.render(context, request))