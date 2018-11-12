import os
import sys
import random
import networkx as nx
import matplotlib.pyplot as plt

if len(sys.argv) != 7:
    print("Format: <name> <# buses> <bus size> <# kids> <# friends> <# rowdy groups>")
    sys.exit(0)

name = sys.argv[1]
num_buses = int(sys.argv[2])
bus_size = int(sys.argv[3])
num_kids = int(sys.argv[4])
num_friends = int(sys.argv[5])
num_rowdy = int(sys.argv[6])

if not os.path.exists('./inputs/' + name + '/'):
    os.makedirs('./inputs/' + name + '/')

G = nx.Graph()

for i in range(num_kids):
    G.add_node(str(i))

for i in range(num_friends):
    a = random.randrange(num_kids)
    b = random.randrange(num_kids)
    edge = (str(a), str(b))
    if edge not in G.edges:
        G.add_edge(*edge)

nx.draw(G, with_labels=True)
plt.savefig('./inputs/' + name + '/graph.png')
nx.write_gml(G, './inputs/' + name + '/graph.gml')

rowdy_groups = []
for i in range(num_rowdy):
    group = []
    for i in range(random.randrange(1, bus_size)):
        kid = random.randrange(num_kids)
        while kid in group:
            kid = random.randrange(num_kids)
        group.append(kid)
    rowdy_groups.append(group)

f = open('./inputs/' + name + '/parameters.txt', 'w')
f.write(str(num_buses) + '\n')
f.write(str(bus_size) + '\n')
for group in rowdy_groups:
    f.write(str([str(kid) for kid in group]) + '\n')
f.close()
