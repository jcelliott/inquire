"""
Document retrieval for question answering
Uses Bing web search API to retrieve documents
"""
from __future__ import absolute_import
import json
import logging as log

try:
    from pymongo import MongoClient
except ImportError:
    pass

from .bing_search_api import BingSearchAPI
from .. import config

def get_documents(question):
    """ get documents for the question by using the 'description' field in Bing results """
    if config.CACHE_DOCS:
        docs = retrieve_cached_docs(question)
        if docs is not None:
            log.debug("got cached docs")
            return docs
    try:
        bing_key = config.BING_API_KEY
    except AttributeError:
        raise Exception("No Bing API key found")

    bing = BingSearchAPI(bing_key)
    params = {
        '$top': config.BING_NUM_RESULTS,
    }
    log.debug("Bing search params: " + str(params))

    # question = preprocess_question(question)

    if config.BING_MOCK_REQUEST:
        log.debug("Making mock request")
        with open(config.BING_MOCK_REQUEST_FILE) as results_data:
            results = json.load(results_data)["d"]["results"]
    else:
        # perform bing search and get results from response (why "d"?)
        results = bing.search_web_json(question, params)["d"]["results"]

    log.debug("Got {} results from Bing".format(len(results)))
    docs = [doc["Description"] for doc in results]
    if config.CACHE_DOCS:
        cache_docs(question, docs)
    return docs

def preprocess_question(question):
    """
    perform any preprocessing of the question to improve search results
    e.g., stop word filtering
    """
    # TODO: look into this more
    return question

def cache_docs(question, docs):
    """ store retrieved documents """
    try:
        cache = MongoClient()[config.MONGO_DB][config.MONGO_COLLECTION]
        obj_id = cache.insert({'question': question, 'docs': docs})
        log.debug("Cached docs: " + str(obj_id))
    except Exception as err:
        log.warn("error caching docs: {}".format(err))

def retrieve_cached_docs(question):
    """ retrieve documents that were stored for the specified question """
    try:
        cache = MongoClient()[config.MONGO_DB][config.MONGO_COLLECTION]
        cached = cache.find_one({'question': question})
        if cached is None:
            return None
        return cached['docs']
    except Exception as err:
        log.warn("error accessing docs cache: {}".format(err))
        return None
