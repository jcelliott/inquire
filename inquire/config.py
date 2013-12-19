import logging
import logging.config

def init(debug=False):
    if debug:
        DEBUG = True
        for logger in LOGGING['loggers']:
            LOGGING['loggers'][logger]['level'] = 'DEBUG'

    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger(__name__)
    logger.debug("Logging level set to DEBUG")

# Run in debug mode
DEBUG = False

# Store the question and answer candidates
CACHE_QUESTION = True

# Windows Azure Marketplace primary account key. Add in config_local.py
BING_API_KEY = ""

# Number of search results to return for each query (max 50)
BING_NUM_RESULTS = 50

# Try to save on API calls by getting results from a file instead of making a real request
BING_MOCK_REQUEST = False
BING_MOCK_REQUEST_FILE = "retrieval/bing_mock_results.json"

# Configuration for nltk Stanford interface (doesn't work very well)
# NER_DIR = os.path.join(os.path.dirname(__file__), "stanford-ner")
# NER_JAR = os.path.join(NER_DIR, "stanford-ner.jar")
# NER_MODEL = "english.muc.7class.distsim.crf.ser.gz"
# NER_MODEL = "english.conll.4class.distsim.crf.ser.gz"
# NER_MODEL_PATH = os.path.join(NER_DIR, "classifiers", NER_MODEL)

# Configuration for Stanford server interface
NER_PORT = 9090


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(module)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'loggers': {
        '': {
            'handlers':['console'],
            'level':'INFO',
        },
    }
}

# Load separate settings file for things that should not be under version control
try:
    execfile('config_local.py')
except IOError:
    pass

