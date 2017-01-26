import multiprocessing
import sys
import traceback

from django.db import Error, transaction

from app.lib import helpers
from app.lib.loaders import loader
from app.lib.nlp import summarizer
from app.lib.utils import parallel
from app.models import *


def aggregate(oqueue, cqueue):
    count = 0
    while True:
        item = cqueue.get()
        if item == parallel.END:
            break
        count += item
    oqueue.put(count)


def do(iqueue, cqueue):
    (review_id, messages) = iqueue.get()

    objects = list()
    with transaction.atomic():
        try:
            for (message_id, message_text) in messages:
                summary = summarizer.Summarizer(message_text).execute()
                for (token, base, frequency, pos) in set(summary):
                    objects.append(Token(
                            message_id=message_id,
                            text=token, base=base, frequency=frequency, pos=pos
                        ))

            if len(objects) > 0:
                Token.objects.bulk_create(objects)
        except Error as err:
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Review  {}\n'.format(review_id))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

    cqueue.put(len(objects))


def stream(review_ids, settings, iqueue):
    for review_id in review_ids:
        messages = list()
        for message in Message.objects.filter(review_id=review_id):
            messages.append((message.id, message.text))
        iqueue.put((review_id, messages))


class TokenLoader(loader.Loader):
    def __init__(self, settings, num_processes, review_ids):
        super(TokenLoader, self).__init__(settings)
        self.num_processes = num_processes
        self.review_ids = review_ids

    def load(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(
                do, aggregate, iqueue, len(self.review_ids), self.num_processes
            )
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream, args=(self.review_ids, self.settings, iqueue)
            )
        process.start()

        return process
