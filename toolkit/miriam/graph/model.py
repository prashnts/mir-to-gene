#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from packrat import catalogue
from pydash import py_

try:
  graph = nx.read_gpickle(catalogue["network"]["computed_sm"]["path"])
except KeyError:
  logger.warn("Graph object unavailable.")
  graph = None

class GraphKit(object):
  """
  Abstraction over the networkx graph.

  API:
    - Return list of miRNAs: GraphKit.mirnas
    - Return list of genes: GraphKit.genes
    - Return the host genes of miRNA, or miRNA the gene is host of:
      GraphKit.host
    - Return the targets of miRNA, or the miRNAs that target the gene:
      GraphKit.target
    - Return the transcript count of the miRNA Host, or Gene:
      GraphKit.transc_count
  """

  def __init__(self, graph):
    self.g = graph

  @property
  def mirnas(self):
    return [k for k, v in self.g.node.items() if v['kind'] == 'MIR']

  @property
  def genes(self):
    return [k for k, v in self.g.node.items() if v['kind'] == 'GEN']

  def host(self, node, *a, **kwa):
    """
    Return the Host Gene, if `node` is miRNA, or, the miRNAs produced by the
    gene if `node` is a Gene.

    Args:
      node (str): Node Name

    Example:
      >>> g.host('MCM7') # is a gene
      ['hsa-miR-106b-5p', 'hsa-miR-93-5p', ...]
    """

    if self.g.node[node]['kind'] == 'MIR':
      return self.g.predecessors(node)
    elif self.g.node[node]['kind'] == 'GEN':
      return self.g.successors(node)
    else:
      raise ValueError("Node is unsupported kind.")

  def target(self, node, *a, **kwa):
    """
    Return the target genes, if `node` is miRNA, or, the miRNAs that target this
    gene if `node` is a Gene.

    Args:
      node (str): Node Name
    """

    if self.g.node[node]['kind'] == 'MIR':
      return self.g.successors(node)
    elif self.g.node[node]['kind'] == 'GEN':
      return self.g.predecessors(node)
    else:
      raise ValueError("Node is unsupported kind.")

  def transc_count(self, node, *a, **kwa):
    if self.g.node[node]['kind'] == 'GEN':
      tc = self.g.node[node]['tc']
    elif self.g.node[node]['kind'] == 'MIR':
      tc = self.transc_count(*self.host(node))
    else:
      raise ValueError("Node is unsupported kind.")

    if type(tc) is int:
      return tc
    else:
      raise ValueError("Transcript Count is not available.")


def depth_limited_nodes(inducers, graph, depth_limit=1):
  def _depth_limited_visits(nbunch, depth=0):
    new_bunch = nbunch[:]
    for node in nbunch:
      c1 = 0
      for h_nei in graph.host(node):
        c1 += 1
        if h_nei not in new_bunch:
          new_bunch.append(h_nei)
        if c1 == 20:
          break

      c2 = 0
      for t_nei in graph.target(node):
        c2 += 1
        if t_nei not in new_bunch:
          new_bunch.append(t_nei)
        if c2 == 20:
          break

    if depth < depth_limit:
      return _depth_limited_visits(new_bunch, depth + 1)
    else:
      return new_bunch
  return _depth_limited_visits(inducers)