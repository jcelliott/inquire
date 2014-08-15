""" Answer extraction for QA """

from operator import itemgetter
from collections import defaultdict
import importlib
import string
import logging as log

import nltk
from ner import SocketNER

from inquire import config

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

class InvalidExtractorError(Exception):
    pass

class BaseExtractor(object):
    def __init__(self, question, docs):
        self.docs = docs
        self.question = question
        self.lem = nltk.stem.wordnet.WordNetLemmatizer()
        self.delete_punctuation_map = dict((ord(char), None) for char in string.punctuation)

    def preprocess(self, pos=False, ner=False, tok_q=True):
        log.debug("preprocessing documents")
        if tok_q:
            self.tok_question = unicode(self.question).translate(self.delete_punctuation_map)
            self.tok_question = nltk.word_tokenize(self.tok_question.lower())
            self.tok_question = [self.lem.lemmatize(word) for word in self.tok_question]
        if pos:
            # self.tok_docs = [nltk.word_tokenize(doc) for doc in self.docs]
            self.pos_docs = [nltk.pos_tag(nltk.word_tokenize(doc)) for doc in self.docs]
        if ner:
            self.ner = SocketNER(host='localhost', port=config.NER_PORT, collapse=False)
            self.ne_docs = [self.ner.get_entities(doc) for doc in self.docs]

    def clean(self, s):
        return self.lem.lemmatize(unicode(s).translate(self.delete_punctuation_map).lower())

    def sort_candidates(self, candidates):
        """
        Takes a dict with frequencies {'a':2, 'b':4, 'c':1} and sorts them.
        Returns the list of sorted candidates with percentages.
        """
        if len(candidates) == 0:
            return None
        # automatically creates nested dict when they don't exist
        cleaned = defaultdict(dict)
        for item, count in candidates.iteritems():
            cleaned[self.clean(item)][item] = count
        results = {}
        for item, options in cleaned.iteritems():
            selected_option, max_count, total_count = None, 0, 0
            for option, count in options.iteritems():
                total_count += count
                if count > max_count:
                    selected_option, max_count = option, count
            results[selected_option] = total_count

        results = sorted(results.iteritems(), key=itemgetter(1), reverse=True)
        total = sum(count for item, count in results)
        # trim to first 10 items
        return [(item, count/float(total)) for item, count in results][:10]

    def answer(self):
        """
        Answer should return a sorted list of answer tuples with their confidence
        """
        return "I don't know how to answer that type of question yet"

class NETagExtractor(BaseExtractor):
    """ extractor that uses named entity tagging """
    def __init__(self, question, docs, tag=None):
        super(NETagExtractor, self).__init__(question, docs)
        if not tag:
            raise InvalidExtractorError("No tag provided for NETagExtractor")
        self.tag = tag

    def answer(self):
        self.preprocess(ner=True)
        candidates = {}
        # count up occurrences of the same NE
        for doc in self.ne_docs:
            for entity in doc:
                # entities come first in this output
                # don't count things that are part of the question
                if entity[0] == self.tag and self.clean(entity[1]) not in self.tok_question:
                    candidates[entity[1]] = candidates.get(entity[1], 0) + 1

        # sort candidates by freqency
        return self.sort_candidates(candidates)

class POSTagExtractor(BaseExtractor):
    """ extractor that uses part-of-speech tagging """
    def __init__(self, question, docs, tags=None):
        super(POSTagExtractor, self).__init__(question, docs)
        if not tags:
            raise InvalidExtractorError("No tag provided for POSTagExtractor")
        self.tags = tags

    def answer(self):
        self.preprocess(pos=True)
        candidates = {}
        # count up occurrences of the same POS
        for doc in self.pos_docs:
            for word in doc:
                # don't count things that are part of the question
                if word[1] in self.tags and self.clean(word[0]) not in self.tok_question:
                    candidates[word[0]] = candidates.get(word[0], 0) + 1

        # sort candidates by freqency
        return self.sort_candidates(candidates)

