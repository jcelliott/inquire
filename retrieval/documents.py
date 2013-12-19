# Document retrieval for question answering
# Uses Bing web search API to retrieve documents

from bing_search_api import BingSearchAPI
import config
import json

import logging as log

def get_documents(question):
    try:
        bing_key = config.BING_API_KEY
    except AttributeError:
        raise Exception("No Bing API key found")

    bing = BingSearchAPI(bing_key)
    params = {
        '$top': config.BING_NUM_RESULTS,
    }
    log.debug("Bing search params: "+str(params))

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
    return docs

# perform any preprocessing of the question to improve search results
# e.g., stop word filtering
def preprocess_question(question):
    # TODO: look into this more
    return question


