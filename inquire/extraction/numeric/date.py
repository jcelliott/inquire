# answer extractor for numeric: date type

from ..extractors import NETagExtractor

TAG = "DATE"

class Extractor(NETagExtractor):
    def __init__(self, question, docs):
        super(Extractor, self).__init__(question, docs, tag=TAG)

