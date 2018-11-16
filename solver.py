import networkx as nx
import os
import random

###########################################
# Change this variable to the path to 
# the folder containing all three input
# size category folders
###########################################
path_to_inputs = "./inputs"

###########################################
# Change this variable if you want
# your outputs to be put in a 
# different folder
###########################################
path_to_outputs = "./outputs"

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

def minimum_cut(graph):
    cutset = set()
    for subgraph in (graph.subgraph(c) for c in nx.connected_components(graph)):
        edges = nx.minimum_edge_cut(subgraph)
        if not edges:
            continue
        if not cutset:
            cutset = edges
        elif len(edges) < len(cutset):
            cutset = edges
    if cutset:
        return cutset
    else:
        raise Exception('no way to make new connected component')

def get_oversized_bus(buses, bus_size):
    for num, bus in enumerate(buses):
        if len(bus) > bus_size:
            return num
    return -1

def get_rowdy_groups(bus, constraints):
    rowdy_groups = []
    for rowdy_group in constraints:
        if rowdy_group.issubset(bus):
            rowdy_groups.append(rowdy_group)
    return rowdy_groups

def score_bus(graph, bus, constraints):
    invalid = set()

    for rowdy_group in constraints:
        if rowdy_group.issubset(bus):
            invalid.update(rowdy_group)

    score = 0
    for kid in sorted(bus.difference(invalid)):
        for neighbor in graph.neighbors(kid):
            if neighbor in bus and neighbor not in invalid and neighbor > kid:
                score += 1
    return score

def solve(graph, num_buses, bus_size, constraints):
    #TODO: Write this method as you like. We'd recommend changing the arguments here as well

    '''
    # random
    buses = [set() for _ in range(num_buses)]
    for kid in graph.nodes():
        bus_num = random.randrange(num_buses)
        while len(buses[bus_num]) == bus_size:
            bus_num = random.randrange(num_buses)
        buses[bus_num].add(kid)

    return [[kid for kid in bus] for bus in buses]
    '''

    if len(graph.nodes()) < num_buses:
        raise Exception('number of nodes less than number of buses')

    # make copy of graph
    copy = graph.copy()

    # turn rowdy groups into sets
    new_constraints = []
    for constraint in constraints:
        new_constraints.append(set(constraint))
    constraints = new_constraints

    # disconnected graph until there are num_buses connected components
    while nx.number_connected_components(copy) < num_buses:
        cutset = minimum_cut(copy)
        copy.remove_edges_from(cutset)

    # assign groups to buses
    buses = []
    for group in nx.connected_components(copy):
        if len(buses) < num_buses:
            buses.append(group)
        else:
            for bus in buses:
                if len(group) + sum(len(bus)) <= bus_size:
                    bus.update(group)
                    break

    oversized = get_oversized_bus(buses, bus_size)
    while oversized >= 0:
        '''
        # remove people from rowdy groups first
        rowdy_groups = get_rowdy_groups(buses[oversized], constraints)
        # sort by descending rowdy group size
        rowdy_groups = sorted(rowdy_groups, key=lambda x: len(x))
        for rowdy_group in rowdy_groups:
            # get kid with lowest degree in rowdy group
            removed_kid = None
            cost = 999999999
            for kid in rowdy_group.intersection(buses[oversized]):
                degree = copy.degree(kid)
                if degree < cost:
                    cost = degree
                    removed_kid = kid

            # bonus from removing removed_kid from bus
            bonus = 0
            for kid in sorted(rowdy_group):
                if kid == removed_kid:
                    continue
                for neighbor in graph.neighbors(kid):
                    if neighbor in buses[oversized] and neighbor != removed_kid and neighbor > kid:
                        bonus += 1
            
            best_bus = None
            best_malus = 999999999
            for num, bus in enumerate(buses):
                if num == oversized or len(bus) == bus_size:
                    continue
                score = score_bus(graph, bus, constraints)
                malus = score - score_bus(graph, bus.union(set(kid)), constraints)
                if malus < best_malus:
                    best_bus = num
                    best_malus = malus

            if best_bus == None:
                break

            if best_malus < bonus:
                print(removed_kid)
                buses[best_bus].add(removed_kid)
                buses[oversized].remove(removed_kid)

        oversized = get_oversized_bus(buses, bus_size)
        '''

        bus = buses[oversized]
        removed_kid = None
        cost = 999999999
        for kid in bus:
            degree = sum([1 if neighbor in bus else 0 for neighbor in graph.neighbors(kid)])
            if degree < cost:
                cost = degree
                removed_kid = kid

        best_bus = None
        best_score = -999999999
        for num, bus in enumerate(buses):
            if num == oversized or len(bus) == bus_size:
                continue
            score = score_bus(graph, bus.union(set(removed_kid)), constraints)
            if score > best_score:
                best_score = score
                best_bus = num

        if best_bus == None:
            break

        buses[best_bus].add(removed_kid)
        buses[oversized].remove(removed_kid)

        oversized = get_oversized_bus(buses, bus_size)

    print(buses)
    


    '''
    # split rowdy groups by removing person with least number of friends
    rowdy_groups = get_rowdy_groups(copy, constraints)
    while rowdy_groups:
        success = fix

    oversized = get_oversized_component(copy, bus_size)
    while oversized:
    '''
    
    return [[kid for kid in bus] for bus in buses]


def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    size_categories = ["small", "medium", "large"]
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
            solution = solve(graph, num_buses, size_bus, constraints)
            output_file = open(output_category_path + "/" + input_name + ".out", "w")

            for bus in solution:
            	output_file.write(str(bus) + '\n')

            output_file.close()

if __name__ == '__main__':
    main()


