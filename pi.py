import sys
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatus, PULP_CBC_CMD
from load_graphs import load_adjacency_matrixes
from solutions import Solution, OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN

INF = None

def add_if_a_true_then_b_c_equal(prob, a, b, c):
    prob += (1 - a) * INF + b >= c
    prob += (1 - a) * INF + c >= b


class Variables:
    def __init__(self):
        self.edges = {}
        self.seeds = {}
        self.groups = {}

    def create_edge(self, i, j):
        if i > j:
            i, j = j, i
        elif i == j:
            raise f"Cannot create edge {i} {j}"

        name = f"edges_{i}_{j}"
        self.edges[name] = LpVariable(name, cat="Binary")

    def get_edge(self, i, j):
        if i > j:
            i, j = j, i

        name = f"edges_{i}_{j}"
        if name not in self.edges:
            raise f"Invalid edge {i} {j}"
        return self.edges[name]
    
    def create_seed(self, i):
        name = f"seed_{i}"
        self.seeds[name] = LpVariable(name, cat="Binary")

    def get_seed(self, i):
        name = f"seed_{i}"
        if name not in self.seeds:
            raise f"Invalid seed {i}"
        return self.seeds[name]
    
    def create_group(self, i):
        name = f"vertex_group_{i}"
        self.groups[name] = LpVariable(name)
    
    def get_group(self, i):
        name = f"vertex_group_{i}"
        if name not in self.groups:
            raise f"Invalid group {i}"
        return self.groups[name]

def maximum_disconnected_matching(g, num_components, timeout):
    global INF

    n = len(g)
    INF = n

    prob = LpProblem("Maximum_Disconnected_Matching", LpMaximize)
    variables = Variables()

    vertices_that_can_be_seeds = [False] * n

    for i in range(n):
        for j in range(i + 1, n):
            if g[i][j]:
                variables.create_edge(i, j)
                vertices_that_can_be_seeds[i] = True
                vertices_that_can_be_seeds[j] = True
    
    for i in range(n):
        if vertices_that_can_be_seeds[i]:
            variables.create_seed(i)
            variables.create_group(i)
    
    # Each vertex can have at most one selected edge
    for i in range(n):
        prob += lpSum(variables.get_edge(i, j) for j in range(n) if g[i][j]) <= 1

    # num_components seeds must be selected
    prob += lpSum(variables.get_seed(i) for i in range(n) if vertices_that_can_be_seeds[i]) == num_components

    # Vertex can belong to a group only if it has an edge
    for i in range(n):
        if vertices_that_can_be_seeds[i]:
            edges = [variables.get_edge(i, j) for j in range(n) if g[i][j]]
            prob += variables.get_group(i) >= 0
            prob += variables.get_group(i) <= lpSum(edges) * INF

    for i in range(n):
        if vertices_that_can_be_seeds[i]:
            add_if_a_true_then_b_c_equal(prob, variables.get_seed(i), variables.get_group(i), i + 1)

    for i in range(n):
        for j in range(i + 1, n):
            if g[i][j]:
                edges_i = [variables.get_edge(i, k) for k in range(n) if g[i][k]]
                edges_j = [variables.get_edge(j, k) for k in range(n) if g[j][k]]
                prob += variables.get_group(i) + ((1 - lpSum(edges_i)) + (1 - lpSum(edges_j))) * INF >= variables.get_group(j)
                prob += variables.get_group(j) + ((1 - lpSum(edges_i)) + (1 - lpSum(edges_j))) * INF >= variables.get_group(i)
                prob += variables.get_seed(j) <= 1 - lpSum(edges_i)

    # Objective: Maximize the number of selected edges
    prob += lpSum(lpSum(variables.get_edge(i, j) for j in range(i + 1, n) if g[i][j]) for i in range(n))

    # Solve the problem
    prob.solve(PULP_CBC_CMD(msg=False, timeLimit=timeout))

    if LpStatus[prob.status] == "Optimal":
        
        selected_edges = [(i, j) for i in range(n) for j in range(i + 1, n) if g[i][j] and variables.get_edge(i, j).varValue > 0.5]
        return Solution(OPTIMAL, selected_edges, prob.solutionTime)

    elif LpStatus[prob.status] == "Feasible":
        
        selected_edges = [(i, j) for i in range(n) for j in range(i + 1, n) if g[i][j] and variables.get_edge(i, j).varValue > 0.5]
        return Solution(FEASIBLE, selected_edges, prob.solutionTime)

    elif LpStatus[prob.status] == "Infeasible":

        return Solution(INFEASIBLE, None, prob.solutionTime)

    else:
        return Solution(UNKNOWN, None, prob.solutionTime)



def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_file> <output_file>")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    file = open(output_file, "w")
    graphs = load_adjacency_matrixes(input_file)
    for g, num_components in graphs:
        solution = maximum_disconnected_matching(g, num_components, 4)
        solution.log(file)
        file.flush()

if __name__ == "__main__":
    main()
