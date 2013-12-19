# Train a question classifier for QA
from os import path
import sys
import re
import fileinput
from pprint import pprint
from time import time
import argparse
import logging as log

import numpy
from sklearn.datasets.base import Bunch
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.cross_validation import StratifiedKFold, LeaveOneOut
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.externals import joblib

from features import (
    TagVectorizer, NERVectorizer, RelatedWordVectorizer, CustomFeatures, CustomRelWordFeatures
)

MODEL_DIR = path.join(path.dirname(__file__), "data/models")

class Classifier:

    def __init__(self, data=None, model_file="classify.pkl"):
        self.data = data
        self.model_file = model_file
        self.model = self.build_model()

    def build_model(self):
        """
        Create the model (pipeline) with any parameters
        """

        model = Pipeline([
            ('union', FeatureUnion([
                ('words', TfidfVectorizer(max_df=0.25, ngram_range=(1,4),
                    sublinear_tf=True, max_features=5000)),
                ('relword', RelatedWordVectorizer(max_df=0.75, ngram_range=(1,4), 
                    sublinear_tf=True)),
                ('pos', TagVectorizer(max_df=0.75, ngram_range=(1,4), 
                    sublinear_tf=True)),
                # ('ner', NERVectorizer(max_df=0.5, ngram_range=(1,4), 
                #     sublinear_tf=True)),
                # ('custom', CustomFeatures()),
                # ('custom_relword', CustomRelWordFeatures()),
            ])),

            ('clf', LinearSVC()),
        ])
        return model

    def train_model(self):
        """
        Train the model with extracted features from all the data

        For a sklearn pipeline example, see:
        http://scikit-learn.org/stable/auto_examples/grid_search_text_feature_extraction.html
        """
        log.debug("Training model...")
        self.model.fit(self.data.data, self.data.target)

    def save_model(self, model_file=None):
        """
        Save model to disk with joblib's replacement of pickle. See:
        http://scikit-learn.org/stable/tutorial/basic/tutorial.html#model-persistence
        """
        if not model_file:
            model_file = self.model_file
        log.debug("Saving model to file: "+model_file)
        joblib.dump(self.model, path.join(MODEL_DIR, model_file))

    def load_model(self, model_file=None):
        """
        Load a model from disk
        """
        if not model_file:
            model_file = self.model_file
        log.debug("Loading model from file: "+model_file)
        self.model = joblib.load(path.join(MODEL_DIR, model_file))
        return self

    def predict(self, doc):
        """
        Predict the classification of a document with the trained model
        Returns the coarse and fine classes
        """
        qtype = self.model.predict([doc])[0].split(':')
        return qtype[0], qtype[1]

    def test_model(self, n_folds=10, leave_one_out=False):
        """
        Test the model by cross-validating with Stratified k-folds

        For a cross-validation example, see:
        http://scikit-learn.org/stable/auto_examples/plot_roc_crossval.html
        """
        log.debug("Testing model ({} folds)".format(n_folds))
        X = self.data.data
        y = self.data.target
        avg_score = 0.0
        
        if leave_one_out:
            cv = LeaveOneOut(len(y))
        else:
            cv = StratifiedKFold(y, n_folds=n_folds)
        
        for train, test in cv:
            model = self.build_model().fit(X[train], y[train])
            avg_score += model.score(X[test], y[test])

        if leave_one_out:
            avg_score /= len(y)
        else:
            avg_score /= n_folds

        print("Average score: {}".format(avg_score))
        return avg_score

    def search_estimator_params(self):
        """
        Parameter selection to find optimal estimator parameters

        Code from:
        http://scikit-learn.org/stable/auto_examples/grid_search_text_feature_extraction.html
        """
        X = self.data.data
        y = self.data.target

        parameters = {
            'union__words__max_df': (0.25, 0.5, 0.75, 1.0),
            # 'union__words__min_df': (0.1, 0.15, 0.2),
            'union__words__max_features': (None, 5000, 10000, 20000),
            # 'union__words__sublinear_tf': (True, False),
            'union__relword__max_df': (0.5, 0.75, 1.0),
            # 'union__relword__min_df': (0.1, 0.15, 0.2),
            # 'union__relword__max_features': (None, 10000),
            # 'union__relword__sublinear_tf': (True, False),
            'union__pos__max_df': (0.5, 0.75, 1.0),
            'union__pos__max_features': (None, 1000),
            # 'union__pos__sublinear_tf': (True, False),
            # 'union__ner__max_df': (0.25, 0.5, 0.75),
            # 'union__ner__max_features': (None, 10000, 50000),
            # 'union__ner__sublinear_tf': (True, False),

            # 'clf__loss': ('l1', 'l2'),
            # 'clf__penalty': ('l1', 'l2'),
            # 'clf__dual': (True, False),
            # 'clf__tol': (1e-5, 1e-4, 1e-3),
            # 'clf__C': (0.5, 1.0, 1.5)
        }

        # find the best parameters for both the feature extraction and the classifier
        grid_search = GridSearchCV(self.model, parameters, n_jobs=4, verbose=1)

        print("Performing grid search...")
        print("pipeline:", [name for name, _ in self.model.steps])
        print("parameters:")
        pprint(parameters)
        t0 = time()
        grid_search.fit(X, y)
        print("done in %0.3fs" % (time() - t0))
        print()

        print("Best score: %0.3f" % grid_search.best_score_)
        print("Best parameters set:")
        best_parameters = grid_search.best_estimator_.get_params()
        for param_name in sorted(parameters.keys()):
            print("\t%s: %r" % (param_name, best_parameters[param_name]))


def load_data(filenames, coarse=False):
    """
    Load samples from one or more files where the format is:
    COARSE_CATEGORY:fine_category some sample data blah blah

    This is a custom data loader based on the `load_files` function in this code:
    https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/datasets/base.py
    """
    data = []
    target = []
    fine_target = []
    if coarse:
        data_re = re.compile(r'(\w+):(\w+) (.+)')
    else:
        data_re = re.compile(r'(\w+:\w+) (.+)')

    for line in fileinput.input(filenames):
        d = data_re.match(line)
        if not d:
            raise Exception("Invalid format in file {} at line {}".format(fileinput.filename(), 
                            fileinput.filelineno()))
        if coarse:
            target.append(d.group(1))
            fine_target.append(d.group(2))
            data.append(d.group(3))
        else:
            target.append(d.group(1))
            data.append(d.group(2))

    return Bunch(
        data=numpy.array(data),
        target=numpy.array(target),
        target_names=set(target),
    )


if __name__ == "__main__":
    # run from parent dir with `python -m classification.model [args]`
    parser = argparse.ArgumentParser(description='Question type classification')
    parser.add_argument("-t", "--test", help="test the classifier", action="store_true")
    parser.add_argument("-o", "--optimize", help="optimize classifier params", action="store_true")
    parser.add_argument("-e", "--example", help="use example data", action="store_true")
    parser.add_argument("-s", "--save", help="save the trained model to disk", action="store_true")
    parser.add_argument("-f", "--savefile", help="the file where the model should be saved")
    parser.add_argument("-c", "--coarse", help="only train on coarse classes", action="store_true")
    parser.add_argument("-a", "--alldata", help="use all data (training and testing)", action="store_true")
    parser.add_argument("-p", "--predict", help="classify an input question")
    args = parser.parse_args()

    if args.example:
        samples = path.join(path.dirname(__file__), "data/example.txt")
    elif args.alldata:
        samples = path.join(path.dirname(__file__), "data/train_all.txt")
    else:
        samples = path.join(path.dirname(__file__), "data/train_5500.txt")
    data = load_data(samples, coarse=args.coarse)

    if args.test:
        clf = Classifier(data)
        # clf.test_model(n_folds=10)
        clf.test_model(n_folds=4)
        # clf.test_model(leave_one_out=True)
        sys.exit(0)
    
    if args.optimize:
        clf = Classifier(data)
        clf.search_estimator_params()
        sys.exit(0)

    if args.save:
        clf = Classifier(data)
        clf.train_model()
        if args.savefile:
            clf.save_model(model_file=args.savefile)
        else:
            clf.save_model()
        sys.exit(0)

    if args.predict:
        clf = Classifier()
        clf.load_model()
        print(clf.predict(args.predict))
        sys.exit(0)

    # import IPython; IPython.embed()
    print("Nothing to do...")
    sys.exit(1)
