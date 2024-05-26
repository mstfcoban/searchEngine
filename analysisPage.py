import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rank_bm25 import BM25Okapi

import numpy as np

nlp = spacy.load('en_core_web_lg')

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

# Initialize the TF-IDF vectorizer
vectorizer = TfidfVectorizer()

url_weight = 0.5
title_weight = 0.3
description_weight = 0.2

company_keywords = ["ınc", "ınc.", "ltd.", "company", "llc", "corp", "corp.", "corporation", "enterprises"]

new_word = ''

def setWord(word):
    global new_word
    words = []

    for w in word.split(' '):
        if w in company_keywords:
            continue
        words.append(w)

    new_word = ' '.join(words)

def removeStopWords(data):
    title = data['title']
    description = data['description']

    title_tokens = word_tokenize(title)
    filtered_title = [w for w in title_tokens if not w.lower() in stop_words]

    description_tokens = word_tokenize(description)
    filtered_description = [w for w in description_tokens if not w.lower() in stop_words]

    return [filtered_title, filtered_description]

def lemmatization(data):
    title = data['title_without_stop_words']
    description = data['description_without_stop_words']

    lemmatized_title = [lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in title]
    lemmatized_description = [lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in description]

    data['title_lemmatized'] = lemmatized_title
    data['description_lemmatized'] = lemmatized_description

    return [lemmatized_title, lemmatized_description]

def calculateScore(word, data):
    score = 1

    if(len(word.split(' ')) > 1):
        domain_word = word.replace(' ', '')
        url_word = word.replace(' ', '-')

        if domain_word in data['domain']:
            score -= 0.025

        if url_word in data['url']:
            score -= 0.05

    if word in data['keywords']['title']:
        index = data['keywords']['title'].index(word)
        score -= data['keywords']['title_value'][index]

    if word in data['keywords']['description']:
        index = data['keywords']['description'].index(word)
        score -= data['keywords']['description_value'][index]

    for w in new_word.split(' '):
        if w in data['keywords']['url']:
            score -= 0.05

        if w in data['domain']:
            score -= 0.025

        if len(new_word.split(' ')) > 1:
            if w in data['keywords']['title']:
                index = data['keywords']['title'].index(w)
                score -= data['keywords']['title_value'][index]

            if w in data['keywords']['description']:
                index = data['keywords']['description'].index(w)
                score -= data['keywords']['description_value'][index]

    return score

def calculateTFIDF(word, data):
    global url_weight, title_weight, description_weight

    tfidf_matrix_url = vectorizer.fit_transform(data['url'] + [word])
    tfidf_matrix_title = vectorizer.fit_transform(data['title'] + [word])
    tfidf_matrix_description = vectorizer.fit_transform(data['description'] + [word])

    # Separate the document vectors and the query vector
    doc_vectors_url = tfidf_matrix_url[:-1]
    query_vector_url = tfidf_matrix_url[-1]
    doc_vectors_title = tfidf_matrix_title[:-1]
    query_vector_title = tfidf_matrix_title[-1]
    doc_vectors_description = tfidf_matrix_description[:-1]
    query_vector_description = tfidf_matrix_description[-1]

    if query_vector_url.shape[0] == 0 or doc_vectors_url.shape[0] == 0:
        similarities_url = np.zeros((1, len(data['url'])))
    else:
        similarities_url = cosine_similarity(query_vector_url, doc_vectors_url).flatten()

    if query_vector_title.shape[0] == 0 or doc_vectors_title.shape[0] == 0:
        similarities_title = np.zeros((1, len(data['title'])))
    else:
        similarities_title = cosine_similarity(query_vector_title, doc_vectors_title).flatten()

    if query_vector_description.shape[0] == 0 or doc_vectors_description.shape[0] == 0:
        similarities_description = np.zeros((1, len(data['description'])))
    else:
        similarities_description = cosine_similarity(query_vector_description, doc_vectors_description).flatten()

    similarities = {
        'url': similarities_url * url_weight,
        'title': similarities_title * title_weight,
        'description': similarities_description * description_weight,
    }

    return similarities

def rankeAlgo(word, data):
    global url_weight, title_weight, description_weight

    word_tokenized = word.split()

    try:
        # Create BM25 objects
        bm25_url = BM25Okapi(data['url'])
        bm25_title = BM25Okapi(data['title'])
        bm25_description = BM25Okapi(data['description'])

        bm25_url_scores = bm25_url.get_scores(word_tokenized)
        bm25_title_scores = bm25_title.get_scores(word_tokenized)
        bm25_description_scores = bm25_description.get_scores(word_tokenized)
    except:
        bm25_url_scores = np.zeros((1, len(data['url'])))
        bm25_title_scores = np.zeros((1, len(data['title'])))
        bm25_description_scores = np.zeros((1, len(data['description'])))

    similarities = {
        'url': bm25_url_scores * url_weight,
        'title': bm25_title_scores * title_weight,
        'description': bm25_description_scores * description_weight,
    }

    return similarities
def Ner(data):
    isCompany = False

    doc_title = nlp(data['title'])
    doc_description = nlp(data['description'])

    label_title = [e.label_ for e in doc_title.ents]
    text_title = [e.text.lower() for e in doc_title.ents]
    label_description = [e.label_ for e in doc_description.ents]
    text_description = [e.text.lower() for e in doc_description.ents]

    if 'ORG' in label_title and 'ORG' in label_description:
        isCompany = True

    """for k in text_title:
        if new_word not in k:
            isCompany = False
    for k in text_description:
        if new_word not in k:
            isCompany = False"""

    return {
        'isCompany': isCompany,
    }
