# Feature extractors for question classification

from os import path, listdir
import glob
from itertools import chain, product

import numpy as np
from nltk import pos_tag
# from nltk.tag.stanford import NERTagger
from ner import SocketNER
from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, VectorizerMixin

import config

REL_WORDS_DIR = path.join(path.dirname(__file__), "data/rel_words")

def build_word_lists():
    word_list_files = listdir(REL_WORDS_DIR)
    word_lists = {}
    for wlf in word_list_files:
        if wlf.startswith('.'):
            continue
        with open(path.join(REL_WORDS_DIR, wlf)) as f:
            word_lists[wlf] = [word.strip().lower() for word in f.readlines()]
    return word_lists

class TagVectorizer(TfidfVectorizer):

    def __init__(self, tags_only=False, input='content', encoding='utf-8', charset=None,
                 decode_error='strict', charset_error=None,
                 strip_accents=None, lowercase=True,
                 preprocessor=None, tokenizer=None, analyzer='word',
                 stop_words=None, token_pattern=r"(?u)\b\w\w+\b",
                 ngram_range=(1, 1), max_df=1.0, min_df=1,
                 max_features=None, vocabulary=None, binary=False,
                 dtype=np.int64, norm='l2', use_idf=True, smooth_idf=True,
                 sublinear_tf=False):
        super(TagVectorizer, self).__init__(
            input=input, charset=charset, charset_error=charset_error,
            encoding=encoding, decode_error=decode_error,
            strip_accents=strip_accents, lowercase=lowercase,
            preprocessor=preprocessor, tokenizer=tokenizer, analyzer=analyzer,
            stop_words=stop_words, token_pattern=token_pattern,
            ngram_range=ngram_range, max_df=max_df, min_df=min_df,
            max_features=max_features, vocabulary=vocabulary, binary=False,
            dtype=dtype, norm=norm, use_idf=use_idf, smooth_idf=smooth_idf,
            sublinear_tf=sublinear_tf)

        self.tags_only = tags_only

    def build_analyzer(self):
        """Return a callable that handles preprocessing and tokenization"""

        preprocess = self.build_preprocessor()
        stop_words = self.get_stop_words()
        tokenizer = self.build_tokenizer()
        tokenize = lambda doc: tokenizer(preprocess(self.decode(doc)))

        # nltk pos_tag returns tuples of the form (word, TAG)
        if self.tags_only:
            # We are just interested in the tags here, so we do tagged_tuple[1]
            get_tags = lambda doc: [t[1] for t in pos_tag(tokenize(doc))]
        else:
            # Here we flatten the tuples to get [word, TAG, word, TAG...]
            # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
            get_tags = lambda doc: list(chain.from_iterable(pos_tag(tokenize(doc))))
        return lambda doc: self._word_ngrams(get_tags(doc), stop_words)

class NERVectorizer(TfidfVectorizer):

    def __init__(self, tags_only=True, input='content', encoding='utf-8', charset=None,
                 decode_error='strict', charset_error=None,
                 strip_accents=None, lowercase=True,
                 preprocessor=None, tokenizer=None, analyzer='word',
                 stop_words=None, token_pattern=r"(?u)\b\w\w+\b",
                 ngram_range=(1, 1), max_df=1.0, min_df=1,
                 max_features=None, vocabulary=None, binary=False,
                 dtype=np.int64, norm='l2', use_idf=True, smooth_idf=True,
                 sublinear_tf=False):
        super(NERVectorizer, self).__init__(
            input=input, charset=charset, charset_error=charset_error,
            encoding=encoding, decode_error=decode_error,
            strip_accents=strip_accents, lowercase=lowercase,
            preprocessor=preprocessor, tokenizer=tokenizer, analyzer=analyzer,
            stop_words=stop_words, token_pattern=token_pattern,
            ngram_range=ngram_range, max_df=max_df, min_df=min_df,
            max_features=max_features, vocabulary=vocabulary, binary=False,
            dtype=dtype, norm=norm, use_idf=use_idf, smooth_idf=smooth_idf,
            sublinear_tf=sublinear_tf)

        self.tags_only = tags_only
        # self.tagger = NERTagger(config.NER_MODEL_PATH, config.NER_JAR, encoding=self.encoding)
        self.tagger = SocketNER(host='localhost', port=config.NER_PORT, collapse=False)

    def build_analyzer(self):
        """Return a callable that handles preprocessing and tokenization"""

        # preprocess = self.build_preprocessor()
        # tokenizer = self.build_tokenizer()
        # tokenize = lambda doc: tokenizer(preprocess(self.decode(doc)))

        # get_tags = lambda doc: [tag for tag in self.tagger.get_entities(doc).iterkeys()]

        if self.tags_only:
            get_tags = lambda doc: [t[0] for t in self.tagger.get_entities(doc)]
        else:
            get_tags = lambda doc: list(chain.from_iterable(self.tagger.get_entities(doc)))

        # if self.tags_only:
        # get_tags = lambda doc: [t[1] for t in self.tagger.tag(tokenize(doc))]
        # else:
        #     get_tags = lambda doc: list(chain.from_iterable(self.tagger.tag(tokenize(doc))))
        return lambda doc: self._word_ngrams(get_tags(doc))

class RelatedWordVectorizer(TfidfVectorizer):
    # just create a new string of "rel_word" tags and pass it into a TfidfVectorizer
    def __init__(self, input='content', encoding='utf-8', charset=None,
                 decode_error='strict', charset_error=None,
                 strip_accents=None, lowercase=True,
                 preprocessor=None, tokenizer=None, analyzer='word',
                 stop_words=None, token_pattern=r"(?u)\b\w\w+\b",
                 ngram_range=(1, 1), max_df=1.0, min_df=1,
                 max_features=None, vocabulary=None, binary=False,
                 dtype=np.int64, norm='l2', use_idf=True, smooth_idf=True,
                 sublinear_tf=False):
        super(RelatedWordVectorizer, self).__init__(
            input=input, charset=charset, charset_error=charset_error,
            encoding=encoding, decode_error=decode_error,
            strip_accents=strip_accents, lowercase=lowercase,
            preprocessor=preprocessor, tokenizer=tokenizer, analyzer=analyzer,
            stop_words=stop_words, token_pattern=token_pattern,
            ngram_range=ngram_range, max_df=max_df, min_df=min_df,
            max_features=max_features, vocabulary=vocabulary, binary=False,
            dtype=dtype, norm=norm, use_idf=use_idf, smooth_idf=smooth_idf,
            sublinear_tf=sublinear_tf)

        self.word_lists = build_word_lists()

    def build_analyzer(self):
        """Return a callable that handles preprocessing and tokenization"""

        preprocess = self.build_preprocessor()
        tokenize = self.build_tokenizer()

        return lambda doc: self._word_ngrams(self.build_rel_word_string(
            tokenize(preprocess(self.decode(doc)))))

    def get_rel_word(self, word):
        for rel,words in self.word_lists.iteritems():
            if word in words:
                return rel
        return ""
        
    def build_rel_word_string(self, doc):
        related_words = ""
        for word in doc:
            rel_word = self.get_rel_word(word)
            if rel_word:
                related_words += rel_word + " "
        return related_words.strip()

class CustomFeatures(BaseEstimator):

    # def __init__(self):

    def get_feature_names(self):
        return np.array([
            'first_who', 'first_what', 'first_where', 'first_when', 'first_why',
            'first_how', 'first_which', 'first_in_what', 'first_in_which', 'how_much',
        ])

    def first_word(self, docs, word):
        return [1 if doc.startswith(word) else 0 for doc in docs]

    def fit(self, documents, y=None):
        return self

    def transform(self, documents):
        lower_docs = [doc.lower() for doc in documents]

        first_who = self.first_word(lower_docs, 'who')
        first_what = self.first_word(lower_docs, 'what')
        first_where = self.first_word(lower_docs, 'where')
        first_when = self.first_word(lower_docs, 'when')
        first_why = self.first_word(lower_docs, 'why')
        first_how = self.first_word(lower_docs, 'how')
        first_which = self.first_word(lower_docs, 'which')
        first_in_what = self.first_word(lower_docs, 'in what')
        first_in_which = self.first_word(lower_docs, 'in which')

        # how much|many
        how_much = [1 if doc.startswith('how much') or doc.startswith('how many') 
                else 0 for doc in lower_docs]

        return np.array([
            first_who, first_what, first_where, first_when, first_why, first_how, first_which, 
            first_in_what, first_in_which, 
            how_much,
        ]).transpose()

class CustomRelWordFeatures(BaseEstimator, VectorizerMixin):

    def __init__(self, input='content', encoding='utf-8', charset=None,
                 decode_error='strict', charset_error=None,
                 strip_accents=None,
                 lowercase=True, preprocessor=None, tokenizer=None,
                 stop_words=None, token_pattern=r"(?u)\b\w\w+\b",
                 ngram_range=(1, 1), analyzer='word'):
        self.word_lists = build_word_lists()
        self.input = input
        self.encoding = encoding
        self.decode_error = decode_error
        self.strip_accents = strip_accents
        self.preprocessor = preprocessor
        self.tokenizer = tokenizer
        self.analyzer = analyzer
        self.lowercase = lowercase
        self.token_pattern = token_pattern
        self.stop_words = stop_words
        self.ngram_range = ngram_range

    def get_feature_names(self):
        return np.array([
            'something',
        ])

    def fit(self, documents, y=None):
        return self

    # unordered
    # def collections()

    def get_search_set(self, term):
        """
        Return a list of search terms given an input term. If the given term
        starts with '@' it is a label for a related word set. It will be
        expanded to a list of all words in the corresponding set
        """
        if term[0] == '@':
            # get list from word_lists
            try:
                return self.word_lists[term[1:]]
            except KeyError:
                return []
        else:
            return [term]

    def check_sparse_colloc(self, doc, pattern):
        """
        Check if a document has the collocation indicated by pattern. Sparse
        means that the words do not have to be consecutive to match. For
        example the pattern ['a','b','c'] would match the document ['a','z','b','3','c'].
        """
        if not pattern:
            return 1
        search_set = self.get_search_set(pattern[0])
        for idx, word in enumerate(doc):
            if word in search_set:
                return self.check_sparse_colloc(doc[idx+1:], pattern[1:])
        return 0
    
    def check_colloc(self, doc, pattern):
        """
        Check if a document has the collocation indicated by pattern. The words
        must appear consecutively to match.
        """
        search_set = self.get_search_set(pattern[0])
        for idx, word in enumerate(doc):
            if word in search_set:
                if len(pattern[1:]) > len(doc[idx+1:]):
                    return 0
                for word, pat in zip(doc[idx+1:], pattern[1:]):
                    if word not in self.get_search_set(pat):
                        return 0
                return 1
        return 0

    def collocations(self, pattern_sets, documents, sparse=False):
        """
        Generate a matrix of collocation features from a list of search elements (pattern_sets)

        given pattern_sets = [['a','b','c'], ['1','2']] collocations will generate features
        to indicate the presence of the following patterns in the input documents:
        'a 1', 'a 2', 'b 1', 'b 2', 'c 1', 'c 2'
        
        The input documents will preprocessed and tokenized with functions from VectorizerMixin
        """
        if sparse:
            check = self.check_sparse_colloc
        else:
            check = self.check_colloc
        patterns = product(*pattern_sets)
        collocations = []

        for pattern in patterns:
            pattern_features = []
            for doc in documents:
                pattern_features.append(check(doc, pattern))
            collocations.append(pattern_features)

        return np.array(collocations).transpose()


    def transform(self, documents):
        lower_docs = [doc.lower() for doc in documents]
        analyzer = self.build_analyzer()
        analyzed_docs = [analyzer(doc) for doc in documents]

        sparse_colloc_sets = [
            [['@stand','@term','@abb','@name','@word','@letter','@symbol'],
             ['for']
            ],
            [['how'],
             ['@unit','@peop','@money','@dist','@perc','@dimen','@def','@ord','@time','@weight']
            ],
            [['@Where'],['come'],['from']],
            [['@At'],['age']],
            [['@How'],['much'],['@weight']],
            [['@What'],
             ['@substance','@currency','@religion','@instrument','@last','@other','@code', '@num',
                 '@ord','@speed','@time','@weight','@body','@def','@desc','@quot','@state', '@abb',
                 '@dimen','@plant','@popu','@group','@title','@mount','@dise','@job','@act', 
                 '@prod','@art','@vessel','@food','@anim','@term','@city','@comp','@country',
                 '@date', '@eff','@dist','@event','@lang','@loca','@money','@name','@peop','@perc',
                 '@sport', '@prof','@temp','@title','@univ','@cause','@tech','@letter','@symbol',
                 '@word', '@color',
             ],
            ],
        ]

        colloc_sets = [
            [['@In','@On','@InOn','@At'],['@What']],
            [['how'],['@big','@fast','@last','@temp','@dist','@dimen','@num','@speed']],
            [['when','@How','@Where','@What'],['@presentBe','@singleBe','@pastBe','be','do']],
            [['in'],['the'],['world']],
        ]

        sparse_colloc_res = np.concatenate(
            [self.collocations(c, analyzed_docs, sparse=True) for c in sparse_colloc_sets], axis=1
        )
        colloc_res = np.concatenate(
            [self.collocations(c, analyzed_docs) for c in colloc_sets], axis=1
        )
        return np.append(sparse_colloc_res, colloc_res, axis=1)

