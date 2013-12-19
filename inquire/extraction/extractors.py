# Answer extraction for QA

import logging as log
import importlib

import nltk
from ner import SocketNER

import config

question_types = {
    'DESC': 'description',
    'ENTY': 'entity',
    'ABBR': 'abbreviation',
    'HUM': 'human',
    'LOC': 'location',
    'NUM': 'number',
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
    def __init__(self, docs):
        self.docs = docs

    def preprocess(self):
        log.debug("preprocessing documents")
        self.pos_docs = [nltk.pos_tag(nltk.word_tokenize(doc)) for doc in self.docs]
        self.ner = SocketNER(host='localhost', port=config.NER_PORT, collapse=False)
        self.ne_docs = [self.ner.get_entities(doc) for doc in self.docs]

    def answer(self):
        return "I don't know how to answer that type of question yet"

