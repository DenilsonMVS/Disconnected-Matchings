
from ortools.sat.python import cp_model
from load_graphs import load_adjacency_matrixes
from solutions import Solution, FEASIBLE, INFEASIBLE, OPTIMAL, UNKNOWN
import sys

def pretty_print_graph(g: list[list[bool]]):
    n = len(g)
    for i in range(n):
        print(f"{i + 1}: ", end="")
        for j in range(n):
            if g[i][j]:
                print(j + 1, end=" ")
        print()

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
    
    # Se uma aresta existe, então os vértices i e j não podem ter arestas com outros vértices
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(0, n):
                if k != i and k != j:
                    model.AddImplication(edges[i][j], edges[i][k].Not())
                    model.AddImplication(edges[i][j], edges[k][j].Not())


    # Semente i nasceu no vértice i
    seeds = [model.new_bool_var(f"seed_{i}") for i in range(n)]
    num_seeds = model.new_int_var(0, n, "num_seeds")
    
    model.Add(num_seeds == sum(seeds))
    model.Add(num_seeds >= num_components)

    vertex_group = [model.new_int_var(-1, n - 1, f"vertex_group_{i}") for i in range(n)]

    edge_in_node = [model.new_bool_var(f"edge_in_node_{i}") for i in range(n)]
    for i in range(n):
        model.add_bool_or([edges[i][j] for j in range(n)]).OnlyEnforceIf(edge_in_node[i])
        model.add_bool_and([edges[i][j].Not() for j in range(n)]).OnlyEnforceIf(edge_in_node[i].Not())

    # Se o vértice não estiver no grafo induzido, não faz parte do grupo de nenhuma semente
    for i in range(n):
        model.Add(vertex_group[i] == -1).only_enforce_if(edge_in_node[i].Not())

    # Se a semente nasceu ali, o vértice faz parte do grupo da semente
    for i in range(n):
        model.add(vertex_group[i] == i).only_enforce_if(seeds[i])
    
    # Se vértice é vizinho de outro, os dois devem estar no mesmo grupo
    are_neighbors_list = []
    for i in range(n):
        for j in range(i + 1, n):
            are_neighbors = model.new_bool_var(f"are_neighbors_{i}_{j}")
            are_neighbors_list.append((i, j, are_neighbors))

            model.add_bool_and([edge_in_node[i], edge_in_node[j], g[i][j]]).only_enforce_if(are_neighbors)
            model.add_bool_or([edge_in_node[i].Not(), edge_in_node[j].Not(), not g[i][j], are_neighbors])

            model.add(vertex_group[i] == vertex_group[j]).only_enforce_if(are_neighbors)


    objective = []
    for i in range(n):
        for j in range(i + 1, n):
            objective.append(edges[i][j])
    
    model.maximize(sum(objective))
    
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_workers = 1
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        edges_res = []
        for i in range(n):
            for j in range(i + 1, n):
                if solver.Value(edges[i][j]) == 1:
                    edges_res.append((i, j))
        
        return Solution(OPTIMAL, edges_res, solver.WallTime())

    elif status == cp_model.FEASIBLE:
        edges_res = []
        for i in range(n):
            for j in range(i + 1, n):
                if solver.Value(edges[i][j]) == 1:
                    edges_res.append((i, j))
        
        return Solution(FEASIBLE, edges_res, solver.WallTime())

    elif status == cp_model.INFEASIBLE:
        return Solution(INFEASIBLE, None, solver.WallTime())
    elif status == cp_model.UNKNOWN:
        return Solution(UNKNOWN, None, solver.WallTime())
    else:
        print(status)


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
        

# python3 main.py test_instances/16_2.txt solutions/16_2.txt && python3 main.py test_instances/16_3.txt solutions/16_3.txt && python3 main.py test_instances/16_4.txt solutions/16_4.txt && python3 main.py test_instances/32_2.txt solutions/32_2.txt && python3 main.py test_instances/32_3.txt solutions/32_3.txt && python3 main.py test_instances/32_4.txt solutions/32_4.txt && python3 main.py test_instances/32_8.txt solutions/32_8.txt && python3 main.py test_instances/64_2.txt solutions/64_2.txt && python3 main.py test_instances/64_3.txt solutions/64_3.txt && python3 main.py test_instances/64_4.txt solutions/64_4.txt && python3 main.py test_instances/64_8.txt solutions/64_8.txt && python3 main.py test_instances/64_16.txt solutions/64_16.txt
# python3 main.py test_instances/16_2.txt solutions/16_2.txt && python3 main.py test_instances/16_3.txt solutions/16_3.txt && python3 main.py test_instances/16_4.txt solutions/16_4.txt && python3 main.py test_instances/32_2.txt solutions/32_2.txt && python3 main.py test_instances/32_3.txt solutions/32_3.txt && python3 main.py test_instances/32_4.txt solutions/32_4.txt && python3 main.py test_instances/32_8.txt solutions/32_8.txt
# python3 pi.py test_instances/16_2.txt solutions/16_2.txt && python3 pi.py test_instances/16_3.txt solutions/16_3.txt && python3 pi.py test_instances/16_4.txt solutions/16_4.txt && python3 pi.py test_instances/32_2.txt solutions/32_2.txt && python3 pi.py test_instances/32_3.txt solutions/32_3.txt && python3 pi.py test_instances/32_4.txt solutions/32_4.txt && python3 pi.py test_instances/32_8.txt solutions/32_8.txt

# python3 statatistics.py test_instances/16_2.txt solutions/cp_sat/test1/16_2.txt images/cp_sat/test1/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/cp_sat/test1/16_3.txt images/cp_sat/test1/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/cp_sat/test1/16_4.txt images/cp_sat/test1/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/cp_sat/test1/32_2.txt images/cp_sat/test1/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/cp_sat/test1/32_3.txt images/cp_sat/test1/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/cp_sat/test1/32_4.txt images/cp_sat/test1/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/cp_sat/test1/32_8.txt images/cp_sat/test1/32_8.png

# python3 statatistics.py test_instances/16_2.txt solutions/cp_sat/test2/16_2.txt images/cp_sat/test2/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/cp_sat/test2/16_3.txt images/cp_sat/test2/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/cp_sat/test2/16_4.txt images/cp_sat/test2/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/cp_sat/test2/32_2.txt images/cp_sat/test2/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/cp_sat/test2/32_3.txt images/cp_sat/test2/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/cp_sat/test2/32_4.txt images/cp_sat/test2/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/cp_sat/test2/32_8.txt images/cp_sat/test2/32_8.png

# python3 statatistics.py test_instances/16_2.txt solutions/linear/test1/16_2.txt images/linear/test1/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/linear/test1/16_3.txt images/linear/test1/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/linear/test1/16_4.txt images/linear/test1/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/linear/test1/32_2.txt images/linear/test1/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/linear/test1/32_3.txt images/linear/test1/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/linear/test1/32_4.txt images/linear/test1/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/linear/test1/32_8.txt images/linear/test1/32_8.png

# python3 statatistics.py test_instances/16_2.txt solutions/linear/test2/16_2.txt images/linear/test2/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/linear/test2/16_3.txt images/linear/test2/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/linear/test2/16_4.txt images/linear/test2/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/linear/test2/32_2.txt images/linear/test2/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/linear/test2/32_3.txt images/linear/test2/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/linear/test2/32_4.txt images/linear/test2/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/linear/test2/32_8.txt images/linear/test2/32_8.png

if __name__ == "__main__":
    main()
