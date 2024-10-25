
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
from random import randint
import networkx as nx
import matplotlib.pyplot as plt
import statistics


def generate_graph(num_vertices: int, num_edges: int):
    g = [[False for _ in range(num_vertices)] for _ in range(num_vertices)]
    
    for _ in range(num_edges):
        while True:
            f, t = randint(0, num_vertices - 1), randint(0, num_vertices - 1)
            if f != t and not g[f][t]:
                g[f][t] = True
                g[t][f] = True
                break
    
    return g

def pretty_print_graph(g: list[list[bool]]):
    n = len(g)
    for i in range(n):
        print(f"{i + 1}: ", end="")
        for j in range(n):
            if g[i][j]:
                print(j + 1, end=" ")
        print()
    
def maximum_matching_with_sat(g: list[list[bool]]):
    n = len(g)

    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    edges = [[model.new_bool_var(f"edge_{i}_{j}") for j in range(n)] for i in range(n)]
    
    for i in range(n):
        for j in range(i, n):
            model.Add(edges[i][j] == edges[j][i])

    for i in range(n):
        for j in range(i, n):
            if not g[i][j]:
                model.Add(edges[i][j] == False)
    
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(0, n):
                if k != i and k != j:
                    model.AddImplication(edges[i][j], edges[i][k].Not())
                    model.AddImplication(edges[i][j], edges[k][j].Not())
    
    objective = []
    for i in range(n):
        for j in range(i + 1, n):
            objective.append(edges[i][j])
    
    model.maximize(sum(objective))
    
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return solver.ObjectiveValue()
    
def maximum_matching_with_blossom(g: list[list[bool]]):
    G = nx.Graph()

    for i in range(len(g)):
        for j in range(i + 1, len(g)):
            if g[i][j]:
                G.add_edge(i, j)

    return len(nx.max_weight_matching(G, maxcardinality=True))


def checker(g: list[list[bool]], num_components: int, matching: list[(int, int)]):
    n = len(g)
    adj_list = [[] for _ in range(n)]

    for f, t in matching:
        if not g[f][t]:
            return False
        adj_list[f].append(t)
        adj_list[t].append(f)
    
    for node in adj_list:
        if len(node) > 1:
            return False
        
    induced_graph_list = [[] for _ in range(n)]
    for i in range(n):
        if len(adj_list[i]) >= 1:
            for j in range(n):
                if g[i][j]:
                    induced_graph_list[i].append(j)
        
    color = [-1 for _ in range(n)]

    for i in range(n):
        if color[i] != -1:
            continue
        stack = []
        stack.append(i)
        while len(stack):
            cur = stack.pop()
            if color[cur] != -1:
                continue
            color[cur] = i
            for to in induced_graph_list[cur]:
                stack.append(to)
    
    colors = set()
    for c in color:
        if c != -1:
            colors.add(c)
    
    return len(colors) >= num_components

def maximum_disconnected_matching(g: list[list[bool]], num_components: int, timeout: int):

    n = len(g)

    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    
    
    edges = [[model.new_bool_var(f"edge_{i}_{j}") for j in range(n)] for i in range(n)]
    
    for i in range(n):
        for j in range(i, n):
            model.Add(edges[i][j] == edges[j][i])

    for i in range(n):
        for j in range(i, n):
            if not g[i][j]:
                model.Add(edges[i][j] == False)
    
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(0, n):
                if k != i and k != j:
                    model.AddImplication(edges[i][j], edges[i][k].Not())
                    model.AddImplication(edges[i][j], edges[k][j].Not())


    induced_graph_vertices = [model.new_bool_var(f"induced_vertice_{i}") for i in range(n)]
    induced_graph_edges = [[model.new_bool_var(f"induced_edges_{i}_{j}") for j in range(n)] for i in range(n)]

    # Grafo simétrico
    for i in range(n):
        for j in range(i + 1, n):
            model.Add(induced_graph_edges[i][j] == induced_graph_edges[j][i])

    # Só deve existir vértice se ele estiver no matching
    for i in range(n):
        model.Add(induced_graph_vertices[i] == sum(edges[i]))

    # Aresta existe se e somente se (os dois vértices estão no grafo induzido e ela existia no grafo original)
    for i in range(n):
        for j in range(i + 1, n):
            if not g[i][j]:
                model.add(induced_graph_edges[i][j] == False)
            else:
                model.Add(induced_graph_edges[i][j] == 1).OnlyEnforceIf([induced_graph_vertices[i], induced_graph_vertices[j]])
                model.Add(induced_graph_edges[i][j] == 0).OnlyEnforceIf([induced_graph_vertices[i].Not(), induced_graph_vertices[j].Not()])



    # Semente i nasceu no vértice j
    seeds = [[model.new_bool_var(f"seed_{i}_{j}") for j in range(n)] for i in range(n)]
    seed_exist = [model.new_bool_var(f"seed_exist_{i}") for i in range(n)]
    num_seeds = model.new_int_var(0, n, "num_seeds")

    # Semente só pode nascer em um vértice
    for i in range(n):
        seed = seeds[i]
        model.Add(seed_exist[i] == sum(seeds[i]))
        model.AddAtMostOne(seed)
    
    model.Add(num_seeds == sum(seed_exist))
    model.Add(num_seeds >= num_components)

    vertex_group = [model.new_int_var(-1, n - 1, "vertex_group_{i}") for i in range(n)]

    # Se o vértice não estiver no grafo induzido, não faz parte do grupo de nenhuma semente
    for i in range(n):
        model.Add(vertex_group[i] == -1).only_enforce_if(induced_graph_vertices[i].Not())

    # Se a semente nasceu ali, o vértice faz parte do grupo da semente
    for i in range(n):
        for j in range(n):
            model.add(vertex_group[j] == i).only_enforce_if(seeds[i][j])
    
    # Se vértice é vizinho de outro, os dois devem estar no mesmo grupo
    for i in range(n):
        for j in range(i + 1, n):
            model.add(vertex_group[i] == vertex_group[j]).only_enforce_if(induced_graph_edges[i][j])


    objective = []
    for i in range(n):
        for j in range(i + 1, n):
            objective.append(edges[i][j])
    
    model.maximize(sum(objective))
    
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_workers = 1
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL:

        # print("Grouping:")
        # grouping = []
        # for i in range(n):
        #     grouping.append(solver.Value(vertex_group[i]))
        # print(grouping)

        # print("Matching:")
        edges_res = []
        for i in range(n):
            for j in range(i + 1, n):
                if solver.Value(edges[i][j]) == 1:
                    edges_res.append((i, j))
        # print(edges_res)

        # print("Induced Graph Vertices:")
        # induced_vertices = []
        # for i in range(n):
        #     if solver.Value(induced_graph_vertices[i]) == 1:
        #         induced_vertices.append(i)
        # print(induced_vertices)

        # print("Induced Graph Edges:")
        # induced_edges = []
        # for i in range(n):
        #     for j in range(i + 1, n):
        #         if solver.Value(induced_graph_edges[i][j]) == 1:
        #             induced_edges.append((i, j))
        # print(induced_edges)
        print(f"optimal: {solver.ObjectiveValue()}")

        assert(checker(g, num_components, edges_res))

        return solver.WallTime()
    elif status == cp_model.FEASIBLE:
        edges_res = []
        for i in range(n):
            for j in range(i + 1, n):
                if solver.Value(edges[i][j]) == 1:
                    edges_res.append((i, j))

        assert(checker(g, num_components, edges_res))
        
        print(f"feasible: {solver.ObjectiveValue()}")
    elif status == cp_model.INFEASIBLE:
        print("No solution found")
        return solver.WallTime()
    else:
        print("Timeout")


def benchmark(num_vertices: int, min_num_edges: int, max_num_edges: int, num_samples: int, k: int):
    results = []
    for num_edges in range(min_num_edges, max_num_edges + 1):
        samples = []
        print(num_edges)
        for _ in range(num_samples):
            g = generate_graph(num_vertices, num_edges)
            samples.append(maximum_disconnected_matching(g, k, 10))
        results.append(samples)
    return results

def main():
    min_edges = 0
    max_edges = 100
    results = benchmark(16, min_edges, max_edges, 10, 2)
    
    avg_times = []
    std_devs = []
    tle_counts = []  # To track the number of time limit exceeded samples
    num_edges_list = list(range(min_edges, max_edges + 1))

    for samples in results:
        valid_samples = [s for s in samples if s is not None]
        tle_count = len([s for s in samples if s is None])  # Count the timeouts

        if valid_samples:
            avg_time = statistics.mean(valid_samples)
            std_dev_time = statistics.stdev(valid_samples) if len(valid_samples) > 1 else 0
        else:
            avg_time = 0
            std_dev_time = 0

        avg_times.append(avg_time)
        std_devs.append(std_dev_time)
        tle_counts.append(tle_count)  # Store TLE count for this num_edges

    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(num_edges_list, avg_times, label="Avg Time (s)")
    plt.xlabel("Number of Edges")
    plt.ylabel("Average Execution Time (s)")
    plt.title("Average Execution Time vs Number of Edges")
    plt.grid(True)

    plt.subplot(1, 3, 2)
    plt.plot(num_edges_list, std_devs, label="Std Dev (s)", color="orange")
    plt.xlabel("Number of Edges")
    plt.ylabel("Standard Deviation (s)")
    plt.title("Standard Deviation vs Number of Edges")
    plt.grid(True)

    plt.subplot(1, 3, 3)
    plt.plot(num_edges_list, tle_counts, label="TLE Count", color="red")
    plt.xlabel("Number of Edges")
    plt.ylabel("Number of TLEs")
    plt.title("Time Limit Exceeded (TLE) Count vs Number of Edges")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
