import networkx as nx
import os
import random

from random import choice

###########################################
# Change this variable to the path to
# the folder containing all three input
# size category folders
###########################################
path_to_inputs = "./all_inputs"

###########################################
# Change this variable if you want
# your outputs to be put in a
# different folder
###########################################
path_to_outputs = "./all_outputs"

def parse_input(folder_name):
    '''
        Parses an input and returns the corresponding graph and parameters

        Inputs:
            folder_name - a string representing the path to the input folder

        Outputs:
            (graph, num_buses, size_bus, constraints)
            graph - the graph as a NetworkX object
            num_buses - an integer representing the number of buses you can allocate to
            size_buses - an integer representing the number of students that can fit on a bus
            constraints - a list where each element is a list vertices which represents a single rowdy group
    '''
    graph = nx.read_gml(folder_name + "/graph.gml")
    parameters = open(folder_name + "/parameters.txt")
    num_buses = int(parameters.readline())
    size_bus = int(parameters.readline())
    constraints = []

    for line in parameters:
        line = line[1: -2]
        curr_constraint = [num.replace("'", "") for num in line.split(", ")]
        constraints.append(curr_constraint)

    return graph, num_buses, size_bus, constraints



def solve(graph, num_buses, bus_size, constraints):
    #TODO: Write this method as you like. We'd recommend changing the arguments here as well

    print('start solve')

    num_kids = len(graph.nodes())
    max_bus_size = min(bus_size, num_kids - num_buses + 1)

    for i in range(len(constraints)):
        constraints[i] = set(constraints[i])
    #constraints = sorted(constraints, key=lambda c: -len(c))

    def isrowdy(group):
        for constraint in constraints:
            if constraint.issubset(group):
                return constraint
        return None


    clusters = []
    copy = graph.copy()

    while copy.nodes():
        clustering = nx.clustering(copy)
        start = max([entry for entry in clustering.items()], key=lambda e: e[1])[0]

        print('\tinitial node: ' + start, end='')

        cluster = set([start])
        fringe = set(copy.neighbors(start))

        fgraph = nx.Graph()
        fgraph.add_node(start)
        for node in fringe:
            fgraph.add_node(node)
            for neighbor in copy.neighbors(node):
                if neighbor in cluster:
                    fgraph.add_edge(node, neighbor)

        while fringe and len(cluster) < max_bus_size:
            degrees = fgraph.degree()
            candidates = sorted(fringe, key=lambda node: -(degrees[node] + clustering[node]))
            index = -1
            for i in range(len(candidates)):
                if not isrowdy(cluster.union(set([candidates[i]]))):
                    index = i
                    break

            if index == -1:
                break

            candidate = candidates[index]
            fringe.remove(candidate)
            cluster.add(candidate)
            for neighbor in copy.neighbors(candidate):
                if neighbor in fringe:
                    fgraph.add_edge(candidate, neighbor)
                elif neighbor not in cluster:
                    fringe.add(neighbor)
                    fgraph.add_node(neighbor)
                    for neighbor_neighbor in copy.neighbors(neighbor):
                        if neighbor_neighbor in cluster:
                            fgraph.add_edge(neighbor, neighbor_neighbor)

        cgraph = nx.Graph()
        for node in cluster:
            cgraph.add_node(node)
            for neighbor in copy.neighbors(node):
                if neighbor in cluster:
                    cgraph.add_edge(node, neighbor)
        while False:
            cdegrees = cgraph.degree()
            loneliest = min(cluster, key=lambda node: cdegrees[node])
            fcopy = fgraph.copy()
            fcopy.remove_node(loneliest)
            fdegrees = fcopy.degree()
            friendly_list = sorted(fringe, key=lambda node: -fdegrees[node])
            friendliest = None
            difference = cluster.difference(set([loneliest]))
            for node in friendly_list:
                if fdegrees[node] <= cdegrees[loneliest]:
                    break
                if fdegrees[node] > cdegrees[loneliest] and not isrowdy(difference.union(set([node]))):
                    friendliest = node
                    break
            if not friendliest:
                break
            cgraph.remove_node(loneliest)
            fgraph.add_node(loneliest)
            fgraph.remove_node(friendliest)
            cgraph.add_node(friendliest)
            cluster.remove(loneliest)
            fringe.add(loneliest)
            fringe.remove(friendliest)
            cluster.add(friendliest)
            for neighbor in copy.neighbors(loneliest):
                if neighbor in fringe:
                    fgraph.add_edge(loneliest, neighbor)
                elif neighbor not in cluster:
                    fgraph.add_node(neighbor)
                    for neighbor_neighbor in copy.neighbors(neighbor):
                        if neighbor_neighbor in cluster:
                            fgraph.add_edge(neighbor, neighbor_neighbor)
            for neighbor in copy.neighbors(friendliest):
                if neighbor in cluster:
                    cgraph.add_edge(friendliest, neighbor)

        clusters.append(cluster)
        copy.remove_nodes_from(cluster)
        print('\tsize: ' + str(len(cluster)))


    clusters = sorted(clusters, key=lambda c: -len(c))
    #print(clusters)
    buses = []

    if len(clusters) < num_buses:
        while len(clusters) < num_buses:
            source = 0
            while source + 1 < len(clusters) and len(clusters[source + 1]) > 1:
                source += 1
            subgraph = graph.subgraph(clusters[source])
            degrees = subgraph.degree()
            loneliest = min([node for node in clusters[source]], key=lambda node: degrees[node])
            clusters[source].remove(loneliest)
            clusters.append(set([loneliest]))
        for cluster in clusters:
            buses.append(cluster)
    elif len(clusters) > num_buses:
        for i in range(num_buses - 1):
            buses.append(clusters[i])
        buses.append(set())
        for i in range(num_buses - 1, len(clusters)):
            added = False
            for j in range(num_buses):
                if len(buses[j]) + len(clusters[i]) <= bus_size and not isrowdy(buses[j].union(clusters[i])):
                    buses[j].update(clusters[i])
                    added = True
                    break
            if added:
                continue
            for j in range(num_buses - 1, -1, -1):
                if len(buses[j]) + len(clusters[i]) <= bus_size:
                    buses[j].update(clusters[i])
                    added = True
                    break
            if added:
                continue
            for j in range(num_buses - 1, -1, -1):
                while clusters[i] and len(buses[j]) < bus_size:
                    buses[j].add(clusters[i].pop())
        if not len(buses[-1]):
            source = 0
            while source + 1 < len(buses) and len(buses[source + 1]) > 1:
                source += 1
            subgraph = graph.subgraph(buses[source])
            degrees = subgraph.degree()
            loneliest = min([node for node in buses[source]], key=lambda node: degrees[node])
            buses[source].remove(loneliest)
            buses[-1].add(loneliest)
    else:
        for i in range(num_buses):
            buses.append(clusters[i])



    print('end solve')
    print(buses)

    return [list(bus) for bus in buses]


def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    size_categories = ["medium"]
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    for size in size_categories:
        category_path = path_to_inputs + "/" + size
        output_category_path = path_to_outputs + "/" + size
        category_dir = os.fsencode(category_path)

        if not os.path.isdir(output_category_path):
            os.mkdir(output_category_path)

        for input_folder in os.listdir(category_dir):
            input_name = os.fsdecode(input_folder)
            graph, num_buses, size_bus, constraints = parse_input(category_path + "/" + input_name)
            print('solving', size, input_name)
            solution = solve(graph, num_buses, size_bus, constraints)
            output_file = open(output_category_path + "/" + input_name + ".out", "w")

            for bus in solution:
            	output_file.write(str(bus) + '\n')

            output_file.close()

if __name__ == '__main__':
    main()
