# answer extractor for human: individual type

from ..extractors import BaseExtractor

class Extractor(BaseExtractor):
    def __init__(self, docs):
        super(Extractor, self).__init__(docs)

    def answer(self):
        self.preprocess()
        return "Lars"
