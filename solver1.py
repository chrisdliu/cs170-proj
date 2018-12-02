import networkx as nx
import os

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

# Gets num vertices of greatest degree
def greatest_degree(graph, num=0):
    sorted_vertices = sorted(graph.degree(), key=lambda v:v[1])
    if num:
        return [pair[0] for pair in sorted_vertices[-num:]]
    return [pair[0] for pair in sorted_vertices]

def solve_multiway(graph, num_buses, bus_size, constraints):
    # Multiway cut solution
    # list of vertices that will be in different components
    to_separate = set()
    # add two from each rowdy group to to_separate
    for rowdy_group in constraints:
        if len(rowdy_group > 1):
            to_separate.update(rowdy_group[:2])

    if len(to_separate) > num_buses:
        pass

# greedy solution
def solve_greedy(graph, num_buses, bus_size, constraints):
    sorted_vertices = sorted(graph.degree(), key=lambda v: -v[1])
    nodes = [pair[0] for pair in sorted_vertices]
    unfilled = [[]] * num_buses
    filled = []

    # Avoids rowdy groups
    i = 0
    for rowdy_group in constraints:
        r1, r2 = rowdy_group[0], rowdy_group[1]
        unfilled[i % num_buses].append(r1)
        unfilled[(i + 1) % num_buses].append(r2)
        nodes.remove(r1)
        nodes.remove(r2)

    while nodes:
        nodes[0]

# sort by degree, put in buses
def solve(graph, num_buses, bus_size, constraints):
    sorted_nodes = sorted(graph.degree(), key=lambda v: -v[1])
    nodes = [pair[0] for pair in sorted_nodes]
    smallest = nodes[-num_buses:]
    nodes = nodes[:-num_buses]
    buses = []
    while nodes:
        buses.append(nodes[:bus_size])
        nodes = nodes[bus_size:]
    num_buses_left = num_buses - len(buses)
    rest_of_buses = [[] for _ in range(num_buses_left)]
    for i in range(len(smallest)):
        rest_of_buses[i % len(rest_of_buses)].append(smallest[i])
    buses.extend(rest_of_buses)
    for bus in buses:
        print(bus)
    return buses

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
            solution = solve(graph, num_buses, size_bus, constraints)
            output_file = open(output_category_path + "/" + input_name + ".out", "w")

            #TODO: modify this to write your solution to your
            #      file properly as it might not be correct to
            #      just write the variable solution to a file
            for bus in solution:
            	output_file.write(str(bus) + '\n')

            output_file.close()

if __name__ == '__main__':
    main()
