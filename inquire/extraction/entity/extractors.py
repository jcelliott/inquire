import logging as log

from ..extractors import NoExtractorError, POSTagExtractor

question_types = {
    'animal': 'animal',
    'body': 'body',
    'color': 'color',
    'cremat': 'creative',
    'currency': 'currency',
    'dismed': 'disease-medicine',
    'event': 'event',
    'food': 'food',
    'instru': 'instrument',
    'lang': 'lang',
    'letter': 'letter',
    'other': 'other',
    'plant': 'plant',
    'product': 'product',
    'religion': 'religion',
    'sport': 'sport',
    'substance': 'substance',
    'symbol': 'symbol',
    'techmeth': 'technique',
    'termeq': 'term',
    'veh': 'vehicle',
    'word': 'word',
}

TAGS = ['NNP', 'NNPS', 'NN', 'NNS']
# TAGS = ['NNP', 'NNPS']

class Extractor(POSTagExtractor):
    def __init__(self, question, docs):
        super(Extractor, self).__init__(question, docs, tags=TAGS)

def get_extractor(coarse, fine):
    log.debug("getting fine extractor for '{}: {}'".format(coarse, fine))
    # just use a location NETagExtractor for all location types
    return Extractor

