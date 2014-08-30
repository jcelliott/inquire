""" evaluate inquire's accuracy """
from __future__ import absolute_import, division, print_function
from collections import defaultdict
import fileinput
# from pprint import pprint
from os import path
import logging as log
import re

from ..inquire import answer_question
from .. import config

# config.init(debug=True)
config.init(debug=False)
config.CACHE_DOCS = True

EVAL_DIR = path.dirname(__file__)
ANSWERS_FILE = path.join(EVAL_DIR, 'eval_a.txt')
QUESTIONS_FILE = path.join(EVAL_DIR, 'eval_q.txt')

def get_questions():
    """ load questions from file """
    questions = {}
    for line in fileinput.input(QUESTIONS_FILE):
        q_num, question = line.split(None, 1)
        questions[q_num] = question.strip()
    return questions


def get_answers():
    """ load answer patterns from file """
    answers = defaultdict(list)
    for line in fileinput.input(ANSWERS_FILE):
        q_num, pattern = line.split(None, 1)
        answers[q_num].append(pattern.strip())
    # pprint(dict(answers), indent=4)
    return answers


def evaluate(questions, answers):
    """ evaluate accuracy """
    total = 0
    correct = 0
    confidences = []
    log.warn("evaluating %d questions", len(questions))

    for q_num, question in questions.iteritems():
        print('\n')
        total += 1
        answer, confidence = answer_question(question)
        log.info("%s %s: %s - %.2f", q_num, question, answer, confidence)
        if answer is None:
            continue
        if evaluate_answer(answers[q_num], answer):
            log.info("correct")
            correct += 1
            confidences.append(confidence)
        else:
            log.info("wrong")

    log.warn("evaluated %d questions", total)
    return (correct / total, sum(confidences) / len(confidences))


def evaluate_answer(patterns, answer):
    """ compare a single answer to acceptable patterns """
    if len(patterns) == 0:
        log.error("no patterns found")
    for pattern in patterns:
        log.info("pattern: %s", pattern)
        pattern = r'.*{}.*'.format(pattern)
        if re.match(pattern, answer, flags=re.IGNORECASE):
            return True
    return False


if __name__ == '__main__':
    q = get_questions()
    a = get_answers()
    accuracy, conf = evaluate(q, a)
    print('accuracy: {}\tconfidence: {}'.format(accuracy, conf))
