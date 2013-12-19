import logging as log
import importlib

from ..extractors import NoExtractorError, NETagExtractor

question_types = {
    'city': 'city',
    'country': 'country',
    'mountain': 'mountain',
    'state': 'state',
    'other': 'other',
}

TAG = "LOCATION"

class Extractor(NETagExtractor):
    def __init__(self, question, docs):
        super(Extractor, self).__init__(question, docs, tag=TAG)

def get_extractor(coarse, fine):
    log.debug("getting fine extractor for '{}: {}'".format(coarse, fine))
    # just use a location NETagExtractor for all location types
    return Extractor

