# answer extractor for numeric: money type

from ..extractors import NETagExtractor

TAG = "MONEY"

class Extractor(NETagExtractor):
    def __init__(self, question, docs):
        super(Extractor, self).__init__(question, docs, tag=TAG)

