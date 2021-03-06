import _pickle
import json
import re
import sys
import subprocess
import traceback

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from json import JSONDecodeError

from app.lib.helpers import JSON_NULL
from app.lib.nlp import analyzers

from app.lib.external import (IMPLICATURE_CLASSIFIER_PATH,
                              IMPLICATURE_VECTORIZER_PATH)
from app.lib.external.squinky_corpus.word import _Word


with open(IMPLICATURE_CLASSIFIER_PATH, 'rb') as f:
    CLS = _pickle.load(f)
with open(IMPLICATURE_VECTORIZER_PATH, 'rb') as f:
    VEC = _pickle.load(f)

DEFAULT_IMPLICATURE = {'implicative': JSON_NULL, 'unimplicative': JSON_NULL}


class ImplicatureAnalyzer(analyzers.Analyzer):
    def __init__(self, text, tokens): # pragma: no cover
        super(ImplicatureAnalyzer, self).__init__(text)
        self.tokens = tokens
        self.classifier = CLS
        self.vectorizer = VEC

    def _score(self, sent, tokens): # pragma: no cover
        words = list()
        for i, tok in enumerate(list(tokens)):
            prev = tokens[i-1]['token'] if i-1 >= 0 else None
            next = tokens[i+1]['token'] if i+1 < len(tokens) else None
            w = _Word(tok['token'], tok['pos'], tok['position'], prev, next,
                      tok['chunk'])
            words.append(w)

        feats = dict()
        for word in words:
            feats.update(word.get_features())
        fv = self.vectorizer.transform(feats)
        probs = self.classifier.predict_proba(fv)

        return {"implicative": probs[0][1], "unimplicative": probs[0][0]}

    def analyze(self):  # pragma: no cover
        implicature = DEFAULT_IMPLICATURE.copy()
        if self.text.strip() == '':
            return implicature

        try:
            implicature = self._score(self.text, self.tokens)
        except Exception as error: # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

        return implicature
