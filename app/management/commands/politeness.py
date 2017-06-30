"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing
import json

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, connections
from django.db.models import Q

from app.lib import loaders, taggers
from app.lib.helpers import *
from app.lib.logger import *
from app.models import *

import app.queryStrings as qs

class Command(BaseCommand):
    """
    Sets up command line arguments.
    """
    help = 'Load the database with code review and bug information.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                '--processes', dest='processes', type=int,
                default=settings.CPU_COUNT,
                help='Number of processes to spawn. Default is {}'.format(
                        settings.CPU_COUNT
                    )
            )
        parser.add_argument(
                '--pop', type=str, default='all', dest='population',
                choices=['all', 'fixed', 'missed', 'neutral', 'empty'],
                help='The review IDs to repopulate complexity metrics for. '
                "Defualt is 'all'."
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        population = options['population']
        begin = dt.now()
        try:
            sents = qs.query_all('sentence', ids=False).exclude(text='') \
                      .iterator()

            connections.close_all()
            tagger = taggers.PolitenessTagger(settings, processes, sents)
            tagger.tag()

        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
