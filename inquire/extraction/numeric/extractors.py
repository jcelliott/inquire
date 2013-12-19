import logging as log
import importlib

from ..extractors import NoExtractorError, NETagExtractor

question_types = {
    'code': 'code',
    'count': 'count',
    'date': 'date', # implemented
    'distance': 'distance',
    'money': 'money', # implemented
    'order': 'order',
    'period': 'period',
    'percent': 'percent', # implemented
    'speed': 'speed',
    'temp': 'temp',
    'volsize': 'size',
    'weight': 'weight',
    'other': 'other',
}

def get_extractor(coarse, fine):
    log.debug("getting fine extractor for '{}: {}'".format(coarse, fine))
    try:
        extractor = importlib.import_module(__package__+'.'+question_types[fine])
    except (ImportError, KeyError):
        log.warn("Extractor for fine type '{}: {}' not implemented".format(coarse, fine))
        raise NoExtractorError(coarse, fine)

    return extractor.Extractor

