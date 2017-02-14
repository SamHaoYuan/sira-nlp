"""
@AUTHOR: meyersbs
"""

import random

from django.contrib.postgres import fields
from django.db.models import Count, Sum, Q
from itertools import chain

from app.models import *

ALL_RIDS = []
FIXED_RIDS = []
MISSED_RIDS = []
NEUTRAL_RIDS = []
NM_RIDS = []
NF_RIDS = []
FM_RIDS = []

ALL_MIDS = []
FIXED_MIDS = []
MISSED_MIDS = []
NEUTRAL_MIDS = []
NM_MIDS = []
NF_MIDS = []
FM_MIDS = []

#### TF-IDF ####################################################################
def query_TF_dict(review_id, use_lemma=False):
    """
    Returns the numerator of TF, the number of occurrences of the token in
    the review.
    """
    column = ''
    if use_lemma:
        column = 'lemma'
    else:
        column = 'token'

    queryResults = Token.objects.filter(message__review__id=review_id) \
        .values(column).annotate(tf=Sum('frequency'))

    return queryResults

def query_DF(review_ids, use_lemma=False):
    """
    Returns the denominator of DF, the number of documents in the population
    that contain the token at least once.
    """
    queryResults = None
    if use_lemma:
        queryResults = ReviewLemmaView.objects \
            .filter(review_id__in=review_ids).values('lemma') \
            .annotate(df=Count('lemma')).order_by('-df')
    else:
        queryResults = ReviewTokenView.objects \
            .filter(review_id__in=review_ids).values('token') \
            .annotate(df=Count('token')).order_by('-df')

    return queryResults

#### Messages ##################################################################
def query_mIDs(population):
    """ Passthrough function for determining which queries to run. """
    global ALL_MIDS, FIXED_MIDS, MISSED_MIDS, NEUTRAL_MIDS
    pop_dict = {'all': query_mIDs_all, 'fixed': query_mIDs_fixed,
                'missed': query_mIDs_missed, 'fm': query_mIDs_fm,
                'random': query_mIDs_random, 'nf': query_mIDs_nf,
                'nm': query_mIDs_nm, 'neutral': query_mIDs_neutral}

    ALL_MIDS = query_mIDs_all()
    FIXED_MIDS = query_mIDs_fixed()
    MISSED_MIDS = query_mIDs_missed()
    NEUTRAL_MIDS = list(set(ALL_MIDS) - set(FIXED_MIDS))
    NEUTRAL_MIDS = list(set(NEUTRAL_MIDS) - set(MISSED_MIDS))

    if population in pop_dict.keys():
        return pop_dict[population]()
    else:
        return query_mIDs_year(population)

def query_mIDs_all():
    """ Return a list of all message IDs. """
    global ALL_MIDS
    if len(ALL_MIDS) > 0:
        return ALL_MIDS

    queryResults = Message.objects.all().values_list('id', flat=True)
    ALL_MIDS = list(queryResults)

    return ALL_MIDS

def query_mIDs_random(message_ids, rand):
    """ Returns a list of all review IDs in the corpus. """
    queryResults = list(Message.objects.filter(id__in=message_ids) \
        .order_by('?').values_list('id', flat=True)[0:rand])

    return queryResults

def query_mIDs_fixed():
    """ Returns a list of message IDs that fixed a vulnerability. """
    global FIXED_MIDS
    if len(FIXED_MIDS) > 0:
        return FIXED_MIDS

    review_ids = query_rIDs_fixed()
    queryResults = Message.objects.filter(review_id__in=review_ids) \
        .values_list('id', flat=True)
    FIXED_MIDS = list(queryResults)

    return FIXED_MIDS

def query_mIDs_missed():
    """ Returns a list of message IDs that missed a vulnerability. """
    global MISSED_MIDS
    if len(MISSED_MIDS) > 0:
        return MISSED_MIDS

    review_ids = query_rIDs_missed()
    queryResults = Message.objects.filter(review_id__in=review_ids) \
        .values_list('id', flat=True)
    MISSED_MIDS = list(queryResults)

    return MISSED_MIDS

def query_mIDs_neutral():
    """
    Returns a list of message IDs that have not fixed or missed a vulnerability.
    """
    global NEUTRAL_MIDS
    if len(NEUTRAL_MIDS) > 0:
        return NEUTRAL_MIDS

    missed = query_mIDs_missed()
    fixed = query_mIDs_fixed()
    queryResults = Message.objects \
        .exclude(Q(id__in=missed) | Q(id__in=fixed)) \
        .values_list('id', flat=True)
    NEUTRAL_MIDS = list(queryResults)

    return NEUTRAL_MIDS

def query_mIDs_fm():
    """
    Returns a list of message IDs that have fixed or missed a vulnerability.
    """
    global FM_MIDS
    if len(FM_MIDS) > 0:
        return FM_MIDS

    missed = query_mIDs_missed()
    fixed = query_mIDs_fixed()
    queryResults = Message.objects \
        .filter(Q(id__in=missed) | Q(id__in=fixed)) \
        .values_list('id', flat=True)
    FM_MIDS = list(queryResults)

    return FM_MIDS

def query_mIDs_nf():
    """
    Returns a list of message IDs that have fixed a vulnerability or have not
    missed a vulnerability.
    """
    global NF_MIDS
    if len(NF_MIDS) > 0:
        return NF_MIDS

    missed = query_mIDs_missed()
    queryResults = Message.objects.exclude(id__in=missed) \
        .values_list('id', flat=True)
    NF_MIDS = list(queryResults)

    return NF_MIDS

def query_mIDs_year(year):
    """ Returns a list of message IDs from the specified year. """
    years = [str(i) for i in range(2008, 2017)]
    if year not in years:
        raise ValueError('Received unknown year for query_messages_year().')
    else:
        queryResults = Message.objects.filter(posted__year=int(year)) \
            .values_list('id', flat=True)

    return queryResults

def query_mIDs_nm():
    """
    Returns a list of message IDs that have missed a vulnerability or have not
    fixed a vulnerability.
    """
    global NM_MIDS
    if len(NM_MIDS) > 0:
        return NM_MIDS

    fixed = query_mIDs_fixed()
    queryResults = Message.objects.exclude(id__in=fixed) \
        .values_list('id', flat=True)
    NM_MIDS = list(queryResults)

    return NM_MIDS

def query_mID_text(message_id):
    """ Return the text field of the given message. """
    queryResults = Message.objects.filter(id__exact=message_id) \
        .values_list('text', flat=True)

    return queryResults[0]

#### Reviews ###################################################################
def query_rIDs(population):
    """ Passthrough function for determining which queries to run. """
    global ALL_RIDS, FIXED_RIDS, MISSED_RIDS, NEUTRAL_RIDS
    pop_dict = {'all': query_rIDs_all, 'fixed': query_rIDs_fixed,
                'missed': query_rIDs_missed, 'fm': query_rIDs_fm,
                'random': query_rIDs_random, 'nf': query_rIDs_nf,
                'nm': query_rIDs_nm, 'neutral': query_rIDs_neutral}

    ALL_RIDS = query_rIDs_all()
    FIXED_RIDS = query_rIDs_fixed()
    MISSED_RIDS = query_rIDs_missed()
    NEUTRAL_RIDS = list(set(ALL_RIDS) - set(FIXED_RIDS))
    NEUTRAL_RIDS = list(set(NEUTRAL_RIDS) - set(MISSED_RIDS))

    if population in pop_dict.keys():
        return pop_dict[population]()
    else:
        return query_rIDs_year(population)

def query_rIDs_all():
    """ Returns a list of all review IDs in the corpus. """
    global ALL_RIDS
    if len(ALL_RIDS) > 0:
        return ALL_RIDS
    queryResults = Review.objects.all().values_list('id', flat=True)

    ALL_RIDS = list(queryResults)

    return ALL_RIDS

def query_rIDs_random(review_ids, rand):
    """ Returns a list of all review IDs in the corpus. """
    queryResults = list(Review.objects.filter(id__in=review_ids) \
        .order_by('?').values_list('id', flat=True)[0:rand])

    return queryResults

def query_rIDs_year(year):
    """ Returns a list of review IDs from the specified year. """
    years = [str(i) for i in range(2008, 2017)]
    if year not in years:
        raise ValueError('Received unknown year for query_rIDs_year().')
    else:
        queryResults = Review.objects.filter(created__year=int(year)) \
            .values_list('id', flat=True)

    return queryResults

def query_rIDs_fixed():
    """ Returns a list of review IDs that fixed a vulnerability. """
    global FIXED_RIDS
    if len(FIXED_RIDS) > 0:
        return FIXED_RIDS

    queryResults = VulnerabilityBug.objects.distinct('bug__review__id') \
        .exclude(bug__review__id__exact=None) \
        .values_list('bug__review__id', flat=True)

    FIXED_RIDS = list(queryResults)

    return FIXED_RIDS

def query_rIDs_missed():
    """ Returns a list of review IDs that missed a vulnerability. """
    global MISSED_RIDS
    if len(MISSED_RIDS) > 0:
        return MISSED_RIDS

    queryResults = Review.objects.filter(missed_vulnerability=True) \
        .values_list('id', flat=True)

    MISSED_RIDS = list(queryResults)

    return MISSED_RIDS

def query_rIDs_neutral():
    """
    Returns a list of review IDs that have not fixed or missed a vulnerability.
    """
    global NEUTRAL_RIDS
    if len(NEUTRAL_RIDS) > 0:
        return NEUTRAL_RIDS

    missed = query_rIDs_missed()
    nm = query_rIDs_nm(ret='raw')
    queryResults = nm.exclude(id__in=missed) \
        .values_list('id', flat=True)

    NEUTRAL_RIDS = list(queryResults)

    return NEUTRAL_RIDS

def query_rIDs_fm():
    """
    Returns a list of review IDs that have fixed or missed a vulnerability.
    """
    global FM_RIDS
    if len(FM_RIDS) > 0:
        return FM_RIDS

    fixed = query_rIDs_fixed()
    missed = query_rIDs_missed()
    FM_RIDS = list(set(fixed) | set(missed))

    return FM_RIDS

def query_rIDs_nf():
    """
    Returns a list of review IDs that have fixed a vulnerability or have not
    missed a vulnerability.
    """
    global ALL_RIDS, NF_RIDS
    if len(NF_RIDS) > 0:
        return NF_RIDS

    missed = query_rIDs_missed()
    NF_RIDS = list(set(ALL_RIDS) - set(missed))

    return NF_RIDS

def query_rIDs_nm():
    """
    Returns a list of review IDs that have missed a vulnerability or have not
    fixed a vulnerability.
    """
    global ALL_RIDS, NM_RIDS
    if len(NM_RIDS) > 0:
        return NM_RIDS

    fixed = query_rIDs_fixed()
    NM_RIDS = list(set(ALL_RIDS) - set(fixed))

    return NM_RIDS

#### Tokens ####################################################################
def query_tokens(review_ids, use_lemma=False):
    if use_lemma:
        queryResults = ReviewLemmaView.objects.distinct('lemma') \
            .filter(review_id__in=review_ids) \
            .values_list('lemma', flat=True)
    else:
        queryResults = ReviewTokenView.objects.distinct('token') \
            .filter(review_id__in=review_ids) \
            .values_list('token', flat=True)

    return queryResults

def query_tokens_all(use_lemma=False):
    if use_lemma:
        queryResults = ReviewLemmaView.objects.distinct('lemma') \
            .values_list('lemma', flat=True)
    else:
        queryResults = ReviewTokenView.objects.distinct('token') \
            .values_list('token', flat=True)

    return queryResults

def query_top_x_tokens(review_ids, x, use_lemma=False):
    message_ids = Message.objects.distinct('id') \
        .filter(review_id__in=review_ids) \
        .values_list('id', flat=True)

    if use_lemma:
        queryResults = Token.objects \
            .filter(message__review__id__in=review_ids) \
            .filter(lemma__iregex=r"\w+") \
            .values('lemma') \
            .annotate(freq=Sum('frequency')) \
            .order_by('-freq') \
            .values_list('lemma', flat=True)
    else:
        queryResults = Token.objects \
            .filter(message__review__id__in=review_ids) \
            .filter(token__iregex=r"\w+") \
            .values('token') \
            .annotate(freq=Sum('frequency')) \
            .order_by('-freq') \
            .values_list('token', flat=True)

    return queryResults[0:x]