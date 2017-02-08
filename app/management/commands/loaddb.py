"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, connections

from app.lib import loaders, taggers
from app.lib.helpers import *
from app.lib.logger import *
from app.models import *


def refresh_view(name):
    with connection.cursor() as cursor:
        cursor.execute('REFRESH MATERIALIZED VIEW {};'.format(name))
        info('  {} refreshed'.format(name))


class Command(BaseCommand):
    """
    Sets up command line arguments.
    """
    help = 'Load the database with code review and bug information.'

    def handle(self, *args, **options):
        """

        """
        begin = dt.now()
        try:
            info('loaddb Command')
            info('  Years: {}'.format(settings.YEARS))

            loader = loaders.BugLoader(settings)
            count = loader.load()
            info('  {} bugs loaded'.format(count))
            loader = loaders.VulnerabilityLoader(settings)
            count = loader.load()
            info('  {} vulnerabilities loaded'.format(count))
            loader = loaders.ReviewLoader(settings)
            count = loader.load()
            info('  {} reviews loaded'.format(count))

            tagger = taggers.MissedVulnerabilityTagger(settings)
            count = tagger.tag()
            info('  {} reviews tagged as missed a vulnerability'.format(count))

            ids = list(Review.objects.all().values_list('id', flat=True))
            connections.close_all()  # Hack
            loader = loaders.MessageLoader(settings, 8, ids)
            count = loader.load()
            info('  {} messages loaded'.format(count))
            loader = loaders.TokenLoader(settings, 8, ids)
            count = loader.load()
            info('  {} tokens loaded'.format(count))

            with multiprocessing.Pool(2) as pool:
                pool.map(refresh_view, ['vw_review_token', 'vw_review_lemma'])
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
