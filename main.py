
# from ortools.init.python import init
from ortools.sat.python import cp_model
from random import randint
import networkx as nx


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


def maximum_disconnected_matching(g: list[list[bool]], num_components: int):

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
    
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:

        print("Grouping:")
        grouping = []
        for i in range(n):
            grouping.append(solver.Value(vertex_group[i]))
        print(grouping)

        print("Matching:")
        edges_res = []
        for i in range(n):
            for j in range(i + 1, n):
                if solver.Value(edges[i][j]) == 1:
                    edges_res.append((i, j))
        print(edges_res)

        print("Induced Graph Vertices:")
        induced_vertices = []
        for i in range(n):
            if solver.Value(induced_graph_vertices[i]) == 1:
                induced_vertices.append(i)
        print(induced_vertices)

        print("Induced Graph Edges:")
        induced_edges = []
        for i in range(n):
            for j in range(i + 1, n):
                if solver.Value(induced_graph_edges[i][j]) == 1:
                    induced_edges.append((i, j))
        print(induced_edges)

        return solver.ObjectiveValue()


def main():
    g = generate_graph(100, 125)
    n = len(g)

    for i in range(n):
        print(f"{i}: ", end="")
        for j in range(n):
            if g[i][j]:
                print(f"{j} ", end="")
        print()

    print(maximum_matching_with_blossom(g))
    print(maximum_matching_with_sat(g))
    print(maximum_disconnected_matching(g, 3))

    # solver = pywraplp.Solver.CreateSolver("SAT")


if __name__ == "__main__":
    main()
