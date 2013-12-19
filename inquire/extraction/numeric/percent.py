# answer extractor for numeric: percent type

from ..extractors import NETagExtractor

TAG = "PERCENT"

class Extractor(NETagExtractor):
    def __init__(self, question, docs):
        super(Extractor, self).__init__(question, docs, tag=TAG)

