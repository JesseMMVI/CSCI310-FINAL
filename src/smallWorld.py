# from https://runestone.academy/ns/books/published/pythonds/BasicDS/ImplementingaQueueinPython.html
# from https://runestone.academy/ns/books/published/pythonds/Graphs/Implementation.html

"""
smallWorld.py
====================================
Implements a Watts–Strogatz small-world graph model and computes average shortest path lengths. Plots the results using Matplotlib.

Provides:

- A rewiring function to construct Watts–Strogatz graphs

- A BFS-based average shortest path length calculator

- A plotting function for path length vs. rewiring probability

| Author: Jesse Gerth
| Date: 2025 November 25
"""

import random
import matplotlib.pyplot as plt

class Vertex:
  def __init__(self,key):
    self.id = key
    self.connectedTo = {}

  def addNeighbor(self,nbr,weight=0):
    self.connectedTo[nbr] = weight

  def __str__(self):
    return str(self.id) + ' connectedTo: ' + str([x.id for x in self.connectedTo])

  def getConnections(self):
    return self.connectedTo.keys()

  def getId(self):
    return self.id

  def getWeight(self,nbr):
    return self.connectedTo[nbr]

class Graph:
  def __init__(self):
    self.vertList = {}
    self.numVertices = 0

  def addVertex(self,key):
    self.numVertices = self.numVertices + 1
    newVertex = Vertex(key)
    self.vertList[key] = newVertex
    return newVertex

  def getVertex(self,n):
    if n in self.vertList:
      return self.vertList[n]
    else:
      return None

  def __contains__(self,n):
    return n in self.vertList

  def addEdge(self,f,t,weight=0):
    if f not in self.vertList:
      nv = self.addVertex(f)
    if t not in self.vertList:
      nv = self.addVertex(t) 
    self.vertList[f].addNeighbor(self.vertList[t], weight)
    self.vertList[t].addNeighbor(self.vertList[f], weight)
    
  def deleteEdge(self, f, t):
    if f in self.vertList and t in self.vertList:
      if self.vertList[t] in self.vertList[f].connectedTo:
        del self.vertList[f].connectedTo[self.vertList[t]]
        del self.vertList[t].connectedTo[self.vertList[f]]

  def getVertices(self):
    return self.vertList.keys()

  def __iter__(self):
    return iter(self.vertList.values())

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

def wattsStrogatzGraph(n, k, p):
  """
    Construct a Watts–Strogatz small-world graph.

    Parameters
    ----------
    n : int
        Number of nodes.
    k : int
        Each node is initially connected to k nearest neighbors.
        Must be even.
    p : float
        Rewiring probability in [0, 1].

    Returns
    -------
    Graph
        A small-world graph instance.
    """

  # Checks if parameters are valid
  if p < 0 or p > 1:
    raise ValueError("p must be in [0, 1]")
  
  if k % 2 != 0:
    raise ValueError("k must be even")
  
  if n < k or n < 3:
    raise ValueError("n must be > k and >= 3")
  
  # Creates graph
  g = Graph()
  
  # Adds (n) vertices (amount of people in the network)
  for i in range(n):
    g.addVertex(i)
  
  # Connects each vertex to (k) nearest neighbors (half_k on each side)
  half_k = k // 2
  for i in range(n):
    for offset in range(-half_k, half_k + 1):
      if offset == 0:
        continue
      j = (i + offset) % n
      g.addEdge(i, j)


  # Rewires edges with probability (p)
  for i in range(n):
    neighbors = list(g.getVertex(i).getConnections())
    for nbr in neighbors:
      if nbr.getId() > i:  # Ensure each edge is considered only once
        if random.random() < p:
          newNbrFound = False
          while not newNbrFound:
            newNbrId = random.randint(0, n - 1)
            if newNbrId != i and newNbrId not in [n.getId() for n in g.getVertex(i).getConnections()]:
              newNbrFound = True
              g.deleteEdge(i, nbr.getId())
              g.addEdge(i, newNbrId)

  # tempList = []
  # tempNbr = []
  # for v in g.getVertices():
  #   for nbr in g.getVertex(v).getConnections():
  #     tempNbr.append(nbr.getId())
  #   tempList.append(tempNbr)
  #   tempNbr = []

  # print(tempList)

  return g

def avgShortestPathLength(g=None, n=1000, k=10, p=0.1):
  """
    Compute the average shortest path length of the graph using BFS.

    Parameters
    ----------
    g : Graph, optional
        Pre-constructed graph. If None, a new Watts–Strogatz graph is built.
    n : int
        Number of nodes (only used if g is None).
    k : int
        Number of neighbors (only used if g is None).
    p : float
        Rewiring probability (only used if g is None).

    Returns
    -------
    float
        Average shortest path length across all vertex pairs.
    """

  totalPathLength = 0
  pathCounts = 0

  if g is None:
    g = wattsStrogatzGraph(n, k, p)

  for startVertex in g:
    visited = {startVertex: 0}
    q = Queue()
    q.enqueue(startVertex)

    while not q.isEmpty():
      currentVertex = q.dequeue()
      currentDistance = visited[currentVertex]

      for neighbor in currentVertex.getConnections():
        if neighbor not in visited:
          visited[neighbor] = currentDistance + 1
          q.enqueue(neighbor)
          totalPathLength += currentDistance + 1
          pathCounts += 1

  avgPathLength = totalPathLength / pathCounts if pathCounts > 0 else 0
  return avgPathLength

def clusteringCoefficient(g):
  """
    Compute the clustering coefficient of the graph.

    Parameters
    ----------
    g : Graph
        The graph instance.

    Returns
    -------
    float
        Clustering coefficient C of the graph.
  """
  totalC = 0
  count = 0

  for v in g:
    neighbors = list(v.getConnections())
    k = len(neighbors)

    if k < 2:
      continue

    # Count actual edges among neighbors
    actual = 0
    possible = k * (k - 1) / 2

    neighbor_ids = {n.getId() for n in neighbors}

    for n in neighbors:
      for nn in n.getConnections():
        if nn.getId() in neighbor_ids and nn.getId() > n.getId():
          actual += 1

    totalC += actual / possible
    count += 1

  return totalC / count if count > 0 else 0

def plotSmallWorld(n=1000, k=10, p_values=None, trials=8):
  """
    Plot average shortest path length vs. rewiring probability.

    Parameters
    ----------
    n : int
        Number of nodes in each generated graph.
    k : int
        Initial nearest-neighbor degree.
    p_values : list of float, optional
        List of rewiring probabilities.
    trials : int
        Number of trials per p value.
    """

  if p_values is None:
    p_values = [0.0, 0.00001, 0.000032, 0.0001, 0.00032, 0.001, 0.0032, 0.01, 0.032, 0.1, 0.32, 1.0]
  
  avg_path_lengths = []
  avg_clusterings = []

  for p in p_values:
    avg_length = 0
    avg_C = 0
    for trial in range(trials):
      g = wattsStrogatzGraph(n, k, p)
      avg_length += avgShortestPathLength(g=g)
      avg_C += clusteringCoefficient(g)


    print(f"p={p}, Average Shortest Path Length over {trials} trials: {avg_length / trials}")
    avg_path_lengths.append(avg_length / trials)

    print(f"p={p}, C={avg_C / trials}, L={avg_length / trials}")
    avg_clusterings.append(avg_C / trials)

  

  plt.plot(p_values, avg_path_lengths, marker='o')
  plt.title('Average Shortest Path Length vs Rewiring Probability')
  plt.xlabel('Rewiring Probability (p)')
  plt.ylabel('Average Shortest Path Length')
  plt.xscale('log')
  plt.grid()
  plt.savefig(f'plots/small_world_N{n}_K{k}_Trials{trials}.png')
  plt.show()

  plt.plot(p_values, avg_clusterings, marker='s')
  plt.title('Clustering Coefficient vs Rewiring Probability')
  plt.xlabel('Rewiring Probability (p)')
  plt.ylabel('Clustering Coefficient C')
  plt.xscale('log')
  plt.grid()
  plt.savefig(f'plots/clustering_coefficient_N{n}_K{k}_Trials{trials}.png')
  plt.show()



if __name__ == "__main__":
  """
  Runs if file called as script as opposed to being imported as a library
  """
  plotSmallWorld(n=1000, k=10, trials=8)