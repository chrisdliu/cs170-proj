import networkx as nx
import os
import random as r

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
def solve_bad(graph, num_buses, bus_size, constraints):
    sorted_nodes = sorted(graph.degree(), key=lambda v: -v[1])
    nodes = [pair[0] for pair in sorted_nodes]
    smallest = nodes[-num_buses:]
    nodes = nodes[:-num_buses]
    buses = []
    while nodes:
        buses.append(nodes[:bus_size])
        nodes = nodes[bus_size:]
    num_buses_left = num_buses - len(buses)
    if num_buses_left:
        rest_of_buses = [[] for _ in range(num_buses_left)]
        for i in range(len(smallest)):
            rest_of_buses[i % len(rest_of_buses)].append(smallest[i])
        buses.extend(rest_of_buses)
    for bus in buses:
        print(bus)
    return buses



'''
First, generate a random solution
Calculate its cost using some cost function you've defined
Generate a random neighboring solution
Calculate the new solution's cost
Compare them:
If cnew < cold: move to the new solution
If cnew > cold: maybe move to the new solution
Repeat steps 3-5 above until an acceptable solution is found or you reach some maximum number of iterations.
'''
def solve(graph, num_buses, bus_size, constraints):
    def solve_random():
        buses = [[] for _ in range(num_buses)]
        nodes = list(graph.nodes())
        for bus in buses:
            bus.append(nodes.pop(r.randint(0, len(nodes)-1)))
        for node in nodes:
            b = r.randint(0, num_buses - 1)
            while len(buses[b]) >= bus_size:
                b = r.randint(0, num_buses - 1)
            buses[b].append(node)
        return buses

    def neighbor(buses, distance):
        for _ in range(distance):
            op = r.randint(0, 1)
            # swap operation
            if op == 0:
                b1, b2 = r.sample(range(num_buses), 2)
                b1, b2 = buses[b1], buses[b2]
                s1, s2 = b1.pop(r.randint(0, len(b1))-1), b2.pop(r.randint(0, len(b2))-1)
                b1.append(s2)
                b2.append(s1)
            # move operation
            else:
                to_add, to_remove = r.sample(range(num_buses), 2)
                to_add, to_remove = buses[to_add], buses[to_remove]
                tries = 0
                while (len(to_add) >= bus_size or len(to_remove) < 2) and tries < 10:
                    tries += 1
                    to_add, to_remove = r.sample(range(num_buses), 2)
                    to_add, to_remove = buses[to_add], buses[to_remove]
                if tries < 10:
                    to_add.append(to_remove.pop(r.randint(0, len(to_remove))-1))
        return buses

    def anneal(curr, iterations, goal):
        if graph.number_of_edges() < 1 or num_buses < 2:
            return curr, 0
        best_sol = curr
        best_cost = cost(curr, graph.copy())
        for _ in range(iterations):
            c_old = cost(curr, graph.copy())
            n = neighbor(curr[:], 1)
            c_new = cost(n, graph.copy())
            if c_new >= goal:
                return n, c_new
            elif c_new > c_old:
                curr = n
                c_old = c_new
                if c_new > best_cost:
                    best_sol = curr
                    best_cost = c_new
            else:
                if r.random() < .1:
                    curr = n
                    c_old = c_new
        return best_sol, best_cost

    def cost(buses, graph):
        total_edges = graph.number_of_edges()
        # Create bus assignments
        bus_assignments = {}
        for i in range(num_buses):
            for student in buses[i]:
                bus_assignments[student] = i

        # Remove nodes for rowdy groups which were not broken up
        for i in range(len(constraints)):
            busses = set()
            for student in constraints[i]:
                busses.add(bus_assignments[student])
            if len(busses) <= 1:
                for student in constraints[i]:
                    if student in graph:
                        graph.remove_node(student)

        # score output
        score = 0
        for edge in graph.edges():
            if bus_assignments[edge[0]] == bus_assignments[edge[1]]:
                score += 1
        if total_edges == 0:
            return 0
        score = score / total_edges
        return score

    sol, cost = anneal(solve_random(), 700, 1)
    print(cost)
    return sol

def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    size_categories = ["small"]
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
