from unittest import TestCase

from app.lib.nlp import analyzers


class SentimentAnalyzerTestCase(TestCase):
    def setUp(self):
        pass

    def test_analyze(self):
        data = (
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs. The company said the sale is subject to certain post '
                'closing adjustments, which it did not explain. Reuter'
            )
        expected = {'vpos': 0, 'pos': 0, 'neut': 1, 'neg': 2, 'vneg': 0}
        actual = analyzers.SentimentAnalyzer(data).analyze()
        self.assertEqual(expected, actual, msg=data[:50])

        data = 'The World is an amazing place.'
        expected = {'vpos': 1, 'pos': 0, 'neut': 0, 'neg': 0, 'vneg': 0}
        actual = analyzers.SentimentAnalyzer(data).analyze()
        self.assertEqual(expected, actual, msg=data[:50])

        data = 'The World is a greate place.'
        expected = {'vpos': 0, 'pos': 1, 'neut': 0, 'neg': 0, 'vneg': 0}
        actual = analyzers.SentimentAnalyzer(data).analyze()
        self.assertEqual(expected, actual, msg=data[:50])

        data = 'The subject of this test is sentiment analysis.'
        expected = {'vpos': 0, 'pos': 0, 'neut': 1, 'neg': 0, 'vneg': 0}
        actual = analyzers.SentimentAnalyzer(data).analyze()
        self.assertEqual(expected, actual, msg=data[:50])

        data = 'The World is a terrible place.'
        expected = {'vpos': 0, 'pos': 0, 'neut': 0, 'neg': 1, 'vneg': 0}
        actual = analyzers.SentimentAnalyzer(data).analyze()
        self.assertEqual(expected, actual, msg=data[:50])

        data = 'The World is a disgusting place.'
        expected = {'vpos': 0, 'pos': 0, 'neut': 0, 'neg': 0, 'vneg': 1}
        actual = analyzers.SentimentAnalyzer(data).analyze()
        self.assertEqual(expected, actual, msg=data[:50])