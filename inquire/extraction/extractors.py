# Answer extraction for QA

from operator import itemgetter
import importlib
import logging as log

import nltk
from ner import SocketNER

import config

question_types = {
    'DESC': 'description',
    'ENTY': 'entity',
    'ABBR': 'abbreviation',
    'HUM': 'human',
    'LOC': 'location',
    'NUM': 'numeric',
}

def get_extractor(coarse, fine):
    log.debug("getting coarse extractor for '{}'".format(coarse))
    # http://stackoverflow.com/questions/301134/dynamic-module-import-in-python
    try:
        coarse_extractor = importlib.import_module(__package__+'.'+question_types[coarse])
    except (ImportError, KeyError):
        log.warn("Extractor for coarse type '{}' not implemented".format(coarse))
        raise NoExtractorError(coarse)

    return coarse_extractor.get_extractor(coarse, fine)

class NoExtractorError(Exception):
    pass

class BaseExtractor(object):
    def __init__(self, question, docs):
        self.docs = docs
        self.question = question

    def preprocess(self, pos=False, ner=False, tok_q=True):
        log.debug("preprocessing documents")
        if tok_q:
            self.tok_question = nltk.word_tokenize(self.question)
        if pos:
            # self.tok_docs = [nltk.word_tokenize(doc) for doc in self.docs]
            self.pos_docs = [nltk.pos_tag(nltk.word_tokenize(doc)) for doc in self.docs]
        if ner:
            self.ner = SocketNER(host='localhost', port=config.NER_PORT, collapse=False)
            self.ne_docs = [self.ner.get_entities(doc) for doc in self.docs]

    def sort_candidates(self, candidates):
        """
        Takes a list of candidate tuples with frequencies [('a',2), ('b',4), ('c',1)] or a dict 
        with frequencies {'a':2, 'b':4, 'c':1} and sorts them by frequency.
        Returns the list of sorted candidates with percentages.
        """
        if len(candidates) == 0:
            return None
        if type(candidates) == dict:
            results = sorted(candidates.iteritems(), key=itemgetter(1), reverse=True)
        else: # list
            results = sorted(candidates, key=itemgetter(1), reverse=True)
        total = sum(count for item, count in results)
        return [(item, count/float(total)) for item, count in results]



    def answer(self):
        """
        Answer should return a sorted list of answer tuples with their confidence
        """
        return "I don't know how to answer that type of question yet"

