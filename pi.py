import sys
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatus, PULP_CBC_CMD
from load_graphs import load_adjacency_matrixes
from solutions import Solution, OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN


def add_if_a_true_then_b_c_equal(prob, a, b, c):
    prob += 1 - a + b >= c
    prob += 1 - a + c >= b

def maximum_disconnected_matching(g, num_components, timeout):

    n = len(g)

    prob = LpProblem("Maximum_Disconnected_Matching", LpMaximize)
    edges = [[LpVariable(f"edges_{i}_{j}", cat="Binary") for j in range(n)] for i in range(n)]

    for i in range(n):
        prob += edges[i][i] == 0

    # Symmetric edges
    for i in range(n):
        for j in range(i + 1, n):
            prob += edges[i][j] == edges[j][i]
    
    # Edge selection constraints
    for i in range(n):
        for j in range(i + 1, n):
            prob += edges[i][j] <= g[i][j]

    # Each vertex can have at most one selected edge
    for i in range(n):
        prob += lpSum(edges[i][j] for j in range(n)) <= 1


    seeds = [LpVariable(f"seed_{i}", cat="Binary") for i in range(n)]

    # At least num_components seeds must be selected
    prob += lpSum(seeds) >= num_components

    vertex_group = [[LpVariable(f"vertex_group_{i}_{j}", cat="Binary") for j in range(n)] for i in range(n)]

    # Vertex can belong to a group only if it has an edge
    for i in range(n):
        prob += lpSum(vertex_group[i]) <= lpSum(edges[i])

    for i in range(n):
        prob += seeds[i] == vertex_group[i][i]


    induced_edges = [[LpVariable(f"induced_edge_{i}_{j}", cat="Binary") for j in range(n)] for i in range(n)]

    for i in range(n):
        prob += induced_edges[i][i] == 0

    for i in range(n):
        for j in range(i + 1, n):
            prob += induced_edges[i][j] == induced_edges[j][i]

    for i in range(n):
        for j in range(i + 1, n):
            prob += induced_edges[i][j] >= g[i][j] + lpSum(edges[i]) + lpSum(edges[j]) - 2
            prob += induced_edges[i][j] <= g[i][j]
            prob += induced_edges[i][j] <= lpSum(edges[i])
            prob += induced_edges[i][j] <= lpSum(edges[j])
    
    for i in range(n):
        for j in range(i + 1, n):
            for group in range(n):
                add_if_a_true_then_b_c_equal(prob, induced_edges[i][j], vertex_group[i][group], vertex_group[j][group])

    # Objective: Maximize the number of selected edges
    prob += lpSum(lpSum(edges[i][j] for j in range(i + 1, n)) for i in range(n))

    # Solve the problem
    prob.solve(PULP_CBC_CMD(msg=False, timeLimit=timeout))

    if LpStatus[prob.status] == "Optimal":
        
        selected_edges = [(i, j) for i in range(n) for j in range(i + 1, n) if edges[i][j].varValue > 0.5]
        return Solution(OPTIMAL, selected_edges, prob.solutionTime)

    elif LpStatus[prob.status] == "Feasible": # Nunca vai cair aqui, vai cair em Unknown (não muda as análises feitas)
        
        selected_edges = [(i, j) for i in range(n) for j in range(i + 1, n) if edges[i][j].varValue > 0.5]
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
    # graphs = graphs[-1:]
    for g, num_components in graphs:
        solution = maximum_disconnected_matching(g, num_components, 4)
        solution.log(file)
        file.flush()

if __name__ == "__main__":
    main()
