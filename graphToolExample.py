from graph_tool.all import *

from numpy.random import seed, random
from scipy.linalg import norm
seed_rng(42)
seed(42)
points = random((400, 2))
points[0] = [0, 0]
points[1] = [1, 1]
g, pos = triangulation(points, type="delaunay")
g.set_directed(True)
edges = list(g.edges())
# reciprocate edges
for e in edges:
    g.add_edge(e.target(), e.source())
# The capacity will be defined as the inverse euclidean distance
cap = g.new_edge_property("double")
for e in g.edges():
    cap[e] = min(1.0 / norm(pos[e.target()].a - pos[e.source()].a), 10)
g.edge_properties["cap"] = cap
g.vertex_properties["pos"] = pos
g.save("flow-example.xml.gz")
graph_draw(g, pos=pos, edge_pen_width=prop_to_size(cap, mi=0, ma=3, power=1),output="flow-example.pdf")