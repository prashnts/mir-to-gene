#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import math
import pandas as pd
import networkx as nx
import functools
import itertools

from multiprocessing import Pool
from pydash import py_

from miriam import psql, db

R = 8.314
T = 303

class Ranking(object):
  def __init__(self, tissue, table, **kwa):
    # Thresholds
    self.th_ps2 = kwa.get('th_ps2', 1)
    self.th_ps3 = kwa.get('th_ps3', 1)
    self.__proc = kwa.get('__proc', 4)

    self.tissue = tissue
    self.table = table
    self.__preinit()
    self.__setup_ground()

  def __preinit(self):
    self.ntwkdg = pd.read_sql_table('ntwkdg', psql)
    self.mirna  = pd.read_sql_table('mirn', psql)

    self.exp_dat = pd.read_sql_query(
      'select gene_name, {0} from {1}'.format(self.tissue, self.table),
      psql
    )

  def __do_merge(self):
    """Return Merged Data Segments

    [Caveates] Returned Columns:
      ['mirna', 'gene', 'dg', 'exp_tar', 'host', 'exp_mir']
        0        1       2     3          4       5
    """
    #: Join Target Gene Expressions
    p1 = self.ntwkdg.merge(self.exp_dat, left_on='gene', right_on='gene_name')
    del p1['gene_name']
    p1 = p1.rename(columns={self.tissue: 'exp_tar'})

    #: Join MiRNA's host genes
    p2 = p1.merge(self.mirna, left_on='mirna', right_on='symbol')
    del p2['symbol']

    p3 = p2.merge(self.exp_dat, left_on='host', right_on='gene_name')
    del p3['gene_name']
    p3 = p3.rename(columns={self.tissue: 'exp_mir'})

    del p1
    del p2
    return p3

  def _f_r1(self, x):
    if x[3] == 0:
      return None
    else:
      return math.exp(-x[2] / (R * T)) * (x[5] / x[3])

  def _f_r2(self, x):
    return x[6] * self.g_p2.degree(x[1]) / self.g_p2.degree(x[0])

  def __setup_ground(self):
    """Adds First Ranking to the DataFrame.
    [Caveates] Added column: `r1`, index: 6
    """
    gd = self.__do_merge()

    #: Calculate keq.

    gd['r1'] = self.__coroutine_apply('_f_r1', gd)#  gd.apply(f_r1_p2, axis=1)

    gd_p1 = gd.sort_values('r1', ascending=False)
    gd_p1.index = range(1, len(gd_p1) + 1)
    self.gd_p1 = gd_p1

  def __get_deg_rank(self):
    pd.options.mode.chained_assignment = None
    self.gd_p2 = self.gd_p1.query('r1 > {0}'.format(math.exp(self.th_ps2)))
    self.g_p2 = nx.from_edgelist(self.gd_p2.loc[:,('mirna', 'gene')].values,
        create_using=nx.DiGraph())

    self.gd_p2['r2'] = self.__coroutine_apply('_f_r2', self.gd_p2)

    gd_p3 = self.gd_p2.sort_values('r2', ascending=False)
    gd_p3.index = range(1, len(gd_p3) + 1)
    if self.th_ps3 > 0:
      gd_p3 = gd_p3.query('r2 > {0}'.format(math.exp(self.th_ps3)))
    return gd_p3

  def __srange(self, lim, step, chunks):
    opts = [[i, i+step] for i in range(0, lim, step)]
    a, _ = opts.pop()
    opts.append([a, lim])

    return [opts[i:i+chunks] for i in range(0, len(opts), chunks)]

  def _process_chunk(self, dat):
    func = getattr(self, dat[0])
    return dat[1].apply(func, axis=1)

  def __coroutine_apply(self, func, frame):
    passes = []
    pool = Pool(processes=self.__proc)

    frame_len = int(len(frame) / self.__proc)

    for cx in self.__srange(len(frame), frame_len, self.__proc):
      chunks = [[func, frame[_[0]:_[1]]] for _ in cx]
      res = pool.map(self._process_chunk, chunks)
      passes.append(res)

    pool.close()
    return pd.concat(py_.flatten(passes))

  def patch_ranks(self, threshold_ground=1, threshold_degree=1):
    self.th_ps2 = threshold_ground
    self.th_ps3 = threshold_degree
    self.ranks = self.__get_deg_rank()

  @property
  def report(self):
    if not hasattr(self, 'ranks'):
      self.patch_ranks()
    uniq_mir_p2 = len(self.gd_p2['mirna'].value_counts())
    uniq_mir_p3 = len(self.ranks['mirna'].value_counts())

    uniq_gen_p2 = len(self.gd_p2['gene'].value_counts())
    uniq_gen_p3 = len(self.ranks['gene'].value_counts())

    return {
      'pass_one': {
        'unique_mirnas': uniq_mir_p2,
        'unique_genes': uniq_gen_p2,
        'total_interactions': len(self.gd_p2),
      },
      'pass_two': {
        'unique_mirnas': uniq_mir_p3,
        'unique_genes': uniq_gen_p3,
        'total_interactions': len(self.ranks),
      },
    }

def get_ranks(tissue, namespace, **kwa):
  doc = db['expre_meta'].find_one({'namespace': namespace})
  if doc is not None and tissue in doc['tissues']:
    runner = Ranking(tissue, doc['db'], **kwa)
    return runner
  else:
    raise KeyError("Given tissue and namespace combination is invalid.")

def plot_gen(**kwa):
  obj = get_ranks(**kwa)

  store = []

  for th in itertools.product(range(10), range(10)):
    try:
      obj.patch_ranks(*th)
      store.append(th + (obj.report['pass_two']['total_interactions'],))
    except Exception:
      pass
    print(th)

  return store
