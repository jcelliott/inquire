# answer extractor for human: group type

from ..extractors import NETagExtractor

TAG = "ORGANIZATION"

class Extractor(NETagExtractor):
    def __init__(self, question, docs):
        super(Extractor, self).__init__(question, docs, tag=TAG)

