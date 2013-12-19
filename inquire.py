#!/usr/bin/env python2
# Python question answering
import config
from retrieval import documents
from classification import model

import argparse
import logging as log

def answer_question(question):
    log.info("answering question: "+args.question)
    log.info("retrieving documents...")
    docs = documents.get_documents(question)
    log.info("classifying question...")
    clf = model.Classifier().load_model()
    qtype = clf.predict(question)
    log.info("question classified as: "+str(qtype))
    #answer_candidates(docs)
    #get_answer(candidates)
    log.info("and the answer is... 42!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Answer a question')
    parser.add_argument("question")
    parser.add_argument("-d", "--debug", help="set logger to debug level", action="store_true")
    parser.add_argument("-m", "--mock_search", help="don't make a real search engine request", 
                        action="store_true")
    args = parser.parse_args()
    config.init(debug=args.debug)
    if args.mock_search:
        config.BING_MOCK_REQUEST = True
    answer_question(args.question)

