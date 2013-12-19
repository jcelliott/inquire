# answer extractor for human: individual type

from ..extractors import BaseExtractor

class Extractor(BaseExtractor):
    def __init__(self, question, docs):
        super(Extractor, self).__init__(question, docs)

    def answer(self):
        self.preprocess(ner=True)
        print(self.ne_docs)
        candidates = {}
        # count up occurrences of the same NE
        for doc in self.ne_docs:
            for entity in doc:
                # don't count things that are part of the question
                if entity[0] == 'PERSON' and entity[1] not in self.tok_question:
                    candidates[entity[1]] = candidates.get(entity[1], 0) + 1
        
        # sort candidates by freqency
        return self.sort_candidates(candidates)

