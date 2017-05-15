"""
@AUTHOR: nuthanmunaiah
@AUTHOR: meyersbs
"""

from django.contrib.postgres import fields
from django.db import models


class Review(models.Model):
    """ Defines the schema for the review table. """
    id = models.BigIntegerField(primary_key=True)

    created = models.DateTimeField()
    is_open = models.BooleanField(default=False)
    was_committed = models.BooleanField(default=False)
    missed_vulnerability = models.BooleanField(default=False)
    num_messages = models.PositiveIntegerField(default=0)

    document = fields.JSONField(default=dict)

    # Navigations Fields
    bugs = models.ManyToManyField('Bug', through='ReviewBug')

    class Meta:
        db_table = 'review'


class Bug(models.Model):
    """ Defines the schema for the bug table. """
    id = models.BigIntegerField(primary_key=True)

    type = models.CharField(max_length=25, default='')
    status = models.CharField(max_length=25, default='')

    document = fields.JSONField(default=dict)

    # Navigations Fields
    reviews = models.ManyToManyField('Review', through='ReviewBug')
    vulnerabilities = models.ManyToManyField(
            'Vulnerability', through='VulnerabilityBug'
        )

    class Meta:
        db_table = 'bug'


class ReviewBug(models.Model):
    """
    Defines the schema for the review_bug table, which maps associated reviews
    and bugs to each other.
    """
    review = models.ForeignKey('Review')
    bug = models.ForeignKey('Bug')

    class Meta:
        db_table = 'review_bug'
        unique_together = ('review', 'bug')


class Vulnerability(models.Model):
    """ Defines the schema for the vulnerability table. """
    id = models.CharField(max_length=15, primary_key=True)
    source = models.CharField(max_length=8, default='monorail')

    # Navigation Fields
    bugs = models.ManyToManyField('Bug', through='VulnerabilityBug')

    class Meta:
        db_table = 'vulnerability'


class VulnerabilityBug(models.Model):
    """
    Defines the schema for the vulnerability_bug table, which maps
    vulnerabilities to bugs.
    """
    vulnerability = models.ForeignKey('Vulnerability')
    bug = models.ForeignKey('Bug')

    class Meta:
        db_table = 'vulnerability_bug'
        unique_together = ('vulnerability', 'bug')


class Message(models.Model):
    """ Defines the schema for the message table. """
    id = models.AutoField(primary_key=True)
    posted = models.DateTimeField()
    sender = models.EmailField()
    text = models.TextField(default='')

    # Navigation Fields
    review = models.ForeignKey('Review')

    class Meta:
        db_table = 'message'


class Sentence(models.Model):
    """ Defines the schema for the sentence table. """
    id = models.AutoField(primary_key=True)
    text = models.TextField(default='')

    parses = fields.JSONField(default=dict)
    metrics = fields.JSONField(
            default={'sentiment': {}, 'complexity': {}, 'politeness': {}}
        )

    # Navigation Fields
    message = models.ForeignKey('Message')
    review = models.ForeignKey('Review')

    class Meta:
        db_table = 'sentence'


class Token(models.Model):
    """ Defines the schema for the token table. """
    id = models.AutoField(primary_key=True)

    position = models.PositiveIntegerField()
    token = models.TextField(default='', db_index=True)
    stem = models.TextField(default='', db_index=True)
    lemma = models.TextField(default='', db_index=True)
    pos = models.CharField(max_length=10, default='')
    chunk = models.CharField(max_length=10, default='')

    # Navigation Fields
    sentence = models.ForeignKey('Sentence')

    class Meta:
        db_table = 'token'
        ordering = ['position']


class ReviewTokenView(models.Model):
    """
    Defines the scheme for the vw_review_token materialized view, which links
    every token with its associated reviewID.
    """
    id = models.BigIntegerField(primary_key=True)

    token = models.TextField(default='')
    review_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'vw_review_token'


class ReviewLemmaView(models.Model):
    """
    Defines the scheme for the vw_review_lemma materialized view, which links
    every lemma with its associated reviewID.
    """
    id = models.BigIntegerField(primary_key=True)

    lemma = models.TextField(default='')
    review_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'vw_review_lemma'
