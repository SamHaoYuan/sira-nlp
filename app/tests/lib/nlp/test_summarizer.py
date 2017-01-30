from unittest import TestCase

from app.lib.nlp import summarizer


class SummarizerTestCase(TestCase):
    def setUp(self):
        pass

    def test_execute(self):
        data = (
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs. The company said the sale is subject to certain post '
                'closing adjustments, which it did not explain. Reuter'
            )
        expected = [
                ('Gulf', 'Gulf', 1, 'NNP'),
                ('Applied', 'Applied', 1, 'NNP'),
                ('Technologies', 'Technologies', 1, 'NNPS'),
                ('Inc', 'Inc', 1, 'NNP'),
                ('said', 'said', 2, 'VBD'),
                ('it', 'it', 2, 'PRP'),
                ('sold', 'sold', 1, 'VBD'),
                ('its', 'it', 1, 'PRP$'),
                ('subsidiaries', 'subsidiary', 1, 'NNS'),
                ('engaged', 'engaged', 1, 'VBN'),
                ('in', 'in', 1, 'IN'),
                ('pipeline', 'pipeline', 1, 'NN'),
                ('and', 'and', 1, 'CC'),
                ('terminal', 'terminal', 1, 'JJ'),
                ('operations', 'operation', 1, 'NNS'),
                ('for', 'for', 1, 'IN'),
                ('12.2', '12.2', 1, 'CD'),
                ('mln', 'mln', 1, 'NN'),
                ('dlrs', 'dlrs', 1, 'NN'),
                ('.', '.', 2, '.'),
                ('The', 'The', 1, 'DT'),
                ('company', 'company', 1, 'NN'),
                ('said', 'said', 2, 'VBD'),
                ('the', 'the', 1, 'DT'),
                ('sale', 'sale', 1, 'NN'),
                ('is', 'is', 1, 'VBZ'),
                ('subject', 'subject', 1, 'JJ'),
                ('to', 'to', 1, 'TO'),
                ('certain', 'certain', 1, 'JJ'),
                ('post', 'post', 1, 'NN'),
                ('closing', 'closing', 1, 'NN'),
                ('adjustments', 'adjustment', 1, 'NNS'),
                (',', ',', 1, ','),
                ('which', 'which', 1, 'WDT'),
                ('it', 'it', 2, 'PRP'),
                ('did', 'did', 1, 'VBD'),
                ('not', 'not', 1, 'RB'),
                ('explain', 'explain', 1, 'VB'),
                ('.', '.', 2, '.'),
                ('Reuter', 'Reuter', 1, 'NN'),
            ]
        actual = summarizer.Summarizer(data).execute()

        self.assertEqual(expected, actual)