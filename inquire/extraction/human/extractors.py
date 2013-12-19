import logging as log
import importlib

from ..extractors import NoExtractorError

question_types = {
    'ind': 'individual',
    'gr': 'group',
    'title': 'title',
    'desc': 'description',
}

def get_extractor(coarse, fine):
    log.debug("getting fine extractor for '{}: {}'".format(coarse, fine))
    try:
        extractor = importlib.import_module(__package__+'.'+question_types[fine])
    except (ImportError, KeyError):
        log.warn("Extractor for fine type '{}: {}' not implemented".format(coarse, fine))
        raise NoExtractorError(coarse, fine)

    return extractor.Extractor

