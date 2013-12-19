#!/usr/bin/env python2
# Python question answering
import config
from retrieval import documents
from classification import model
from extraction import get_extractor, NoExtractorError

import argparse
import logging as log

def answer_question(question):
    """
    Main pipeline for question answering
    Takes a question and returns the most likely answer
    """
    log.info("answering question: "+args.question)
    log.info("retrieving documents...")
    docs = documents.get_documents(question)
    log.info("classifying question...")
    clf = model.Classifier().load_model()
    coarse, fine = clf.predict(question)
    log.info("question classified as: {}: {}".format(coarse, fine))
    #answer_candidates(docs)
    try:
        extractor = get_extractor(coarse, fine)
    except NoExtractorError:
        return "I don't know how to answer that type of question yet."
    # returns a sorted list of tuples
    answers = extractor(question, docs).answer()
    if answers == None:
        log.info("No answers found!")
    else:
        log.info("best answer: "+answers[0][0])
        print_answers(answers)
    return answers

def print_answers(answers):
    print("Possible answers:")
    print("-"*30)
    for res in answers:
        print(unicode(u"{0:.2f}\t{1}".format(res[1], res[0])))

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

