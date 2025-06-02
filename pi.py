import sys
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatus, PULP_CBC_CMD
from load_graphs import load_adjacency_matrixes
from solutions import Solution, OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN

INF = None

def add_if_a_true_then_b_c_equal(prob, a, b, c):
    prob += (1 - a) * INF + b >= c
    prob += (1 - a) * INF + c >= b

def maximum_disconnected_matching(g, num_components, timeout):
    global INF

    n = len(g)
    INF = n

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
    prob += lpSum(seeds) == num_components

    vertex_group = [LpVariable(f"vertex_group_{i}") for i in range(n)]


    # Vertex can belong to a group only if it has an edge
    for i in range(n):
        prob += vertex_group[i] >= 0
        prob += vertex_group[i] <= lpSum(edges[i]) * INF

    for i in range(n):
        add_if_a_true_then_b_c_equal(prob, seeds[i], vertex_group[i], i + 1)

    for i in range(n):
        for j in range(i + 1, n):
            prob += vertex_group[i] + ((1 - g[i][j]) + (1 - lpSum(edges[i])) + (1 - lpSum(edges[j]))) * INF >= vertex_group[j]
            prob += vertex_group[j] + ((1 - g[i][j]) + (1 - lpSum(edges[i])) + (1 - lpSum(edges[j]))) * INF >= vertex_group[i]
            prob += seeds[j] <= (1 - g[i][j]) + (1 - lpSum(edges[i]))

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
