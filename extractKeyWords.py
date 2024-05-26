import yake
import wordsegment

wordsegment.load()

max_ngram_size = 3
deduplication_threshold = 0.5
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 10

def extractKeyWords(text, is_url = False):

    if is_url:
        url_words = wordsegment.segment(text)
        return url_words

    kw_extractor = yake.KeywordExtractor(n=max_ngram_size, dedupLim=deduplication_threshold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
    keywords = kw_extractor.extract_keywords(text)

    return keywords