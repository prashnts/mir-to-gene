#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import request
from miRNA import db, app

class Gene(db.Document):
  symbol = db.StringField(unique = True)
  FASTA  = db.StringField()
  names  = db.ListField(db.StringField())

  description       = db.StringField()
  transcript_count  = db.IntField()

  searchable = db.StringField()

  meta = {
    'allow_inheritance': True,
    'strict': False,
  }

  def __unicode__(self):
    return self.symbol

  @property
  def foo(self):
      return "fee"


class miRNAGeneTargetComplex(db.EmbeddedDocument):
  gene      = db.ReferenceField(Gene)
  affinity  = db.FloatField()

  meta = {'allow_inheritance': True, 'strict': False}



class miRNA(db.Document):
  symbol  = db.StringField(unique = True)
  FASTA   = db.StringField()
  host    = db.ReferenceField(Gene)
  targets = db.ListField(db.EmbeddedDocumentField(miRNAGeneTargetComplex))

  mirbase_url = db.StringField()
  transcript_count = db.IntField()

  searchable = db.StringField()

  meta = {'allow_inheritance': True, 'strict': False}

  def __unicode__(self):
    return self.symbol
