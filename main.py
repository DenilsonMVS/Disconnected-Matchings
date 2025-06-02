
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
    
    has_edge = [model.new_bool_var(f"has_edge_{i}") for i in range(n)]
    edges = [[model.new_bool_var(f"edge_{i}_{j}") for j in range(n)] for i in range(n)]
    
    for i in range(n):
        for j in range(i, n):
            model.Add(edges[i][j] == edges[j][i])

    for i in range(n):
        for j in range(i, n):
            if not g[i][j]:
                model.Add(edges[i][j] == False)

    # calculating the value of has_edge
    for i in range(n):
        model.add_bool_or([has_edge[i].Not()] + edges[i])
        for j in range(n):
            model.add_bool_or([has_edge[i], edges[i][j].Not()])
    
    # Se uma aresta existe, então os vértices i e j não podem ter arestas com outros vértices
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(0, n):
                if k != i and k != j:
                    model.AddImplication(edges[i][j], edges[i][k].Not())
                    model.AddImplication(edges[i][j], edges[k][j].Not())


    vertex_group = [[model.new_bool_var(f"vertex_group_{i}_{j}") for j in range(n)] for i in range(n)]
    num_seeds = model.new_int_var(0, n, "num_seeds")
    
    model.Add(num_seeds == sum([vertex_group[i][i] for i in range(n)]))
    model.Add(num_seeds >= num_components)

    for i in range(n):
        for j in range(n):
            for k in range(n):
                if j != k:
                    model.AddImplication(vertex_group[i][j], vertex_group[i][k].Not())

    # Se o vértice não estiver no grafo induzido, não faz parte do grupo de nenhuma semente
    for i in range(n):
        model.AddImplication(has_edge[i].Not(), vertex_group[i][i].Not())

    # Constraint de estarem no mesmo grupo se houver uma aresta entre eles
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(n):
                model.add_bool_or([not g[i][j], has_edge[i].Not(), has_edge[j].Not(), vertex_group[i][k].Not(), vertex_group[j][k]])
                model.add_bool_or([not g[i][j], has_edge[i].Not(), has_edge[j].Not(), vertex_group[i][k], vertex_group[j][k].Not()])

    
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

# python3 statatistics.py test_instances/16_2.txt solutions/cp_sat/test3/16_2.txt images/cp_sat/test3/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/cp_sat/test3/16_3.txt images/cp_sat/test3/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/cp_sat/test3/16_4.txt images/cp_sat/test3/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/cp_sat/test3/32_2.txt images/cp_sat/test3/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/cp_sat/test3/32_3.txt images/cp_sat/test3/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/cp_sat/test3/32_4.txt images/cp_sat/test3/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/cp_sat/test3/32_8.txt images/cp_sat/test3/32_8.png

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

# Obter nova base
# python3 statatistics.py test_instances/16_2.txt solutions/linear/test3/16_2.txt images/linear/test3/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/linear/test3/16_3.txt images/linear/test3/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/linear/test3/16_4.txt images/linear/test3/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/linear/test3/32_2.txt images/linear/test3/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/linear/test3/32_3.txt images/linear/test3/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/linear/test3/32_4.txt images/linear/test3/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/linear/test3/32_8.txt images/linear/test3/32_8.png

# M = n
# python3 statatistics.py test_instances/16_2.txt solutions/linear/test4/16_2.txt images/linear/test4/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/linear/test4/16_3.txt images/linear/test4/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/linear/test4/16_4.txt images/linear/test4/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/linear/test4/32_2.txt images/linear/test4/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/linear/test4/32_3.txt images/linear/test4/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/linear/test4/32_4.txt images/linear/test4/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/linear/test4/32_8.txt images/linear/test4/32_8.png

# k == c
# python3 statatistics.py test_instances/16_2.txt solutions/linear/test5/16_2.txt images/linear/test5/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/linear/test5/16_3.txt images/linear/test5/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/linear/test5/16_4.txt images/linear/test5/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/linear/test5/32_2.txt images/linear/test5/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/linear/test5/32_3.txt images/linear/test5/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/linear/test5/32_4.txt images/linear/test5/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/linear/test5/32_8.txt images/linear/test5/32_8.png

# base
# python3 statatistics.py test_instances/16_2.txt solutions/cp_sat/test4/16_2.txt images/cp_sat/test4/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/cp_sat/test4/16_3.txt images/cp_sat/test4/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/cp_sat/test4/16_4.txt images/cp_sat/test4/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/cp_sat/test4/32_2.txt images/cp_sat/test4/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/cp_sat/test4/32_3.txt images/cp_sat/test4/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/cp_sat/test4/32_4.txt images/cp_sat/test4/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/cp_sat/test4/32_8.txt images/cp_sat/test4/32_8.png

# k == c
# python3 statatistics.py test_instances/16_2.txt solutions/cp_sat/test5/16_2.txt images/cp_sat/test5/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/cp_sat/test5/16_3.txt images/cp_sat/test5/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/cp_sat/test5/16_4.txt images/cp_sat/test5/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/cp_sat/test5/32_2.txt images/cp_sat/test5/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/cp_sat/test5/32_3.txt images/cp_sat/test5/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/cp_sat/test5/32_4.txt images/cp_sat/test5/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/cp_sat/test5/32_8.txt images/cp_sat/test5/32_8.png

# removendo simetria
# python3 statatistics.py test_instances/16_2.txt solutions/linear/test6/16_2.txt images/linear/test6/16_2.png
# python3 statatistics.py test_instances/16_3.txt solutions/linear/test6/16_3.txt images/linear/test6/16_3.png
# python3 statatistics.py test_instances/16_4.txt solutions/linear/test6/16_4.txt images/linear/test6/16_4.png
# python3 statatistics.py test_instances/32_2.txt solutions/linear/test6/32_2.txt images/linear/test6/32_2.png
# python3 statatistics.py test_instances/32_3.txt solutions/linear/test6/32_3.txt images/linear/test6/32_3.png
# python3 statatistics.py test_instances/32_4.txt solutions/linear/test6/32_4.txt images/linear/test6/32_4.png
# python3 statatistics.py test_instances/32_8.txt solutions/linear/test6/32_8.txt images/linear/test6/32_8.png

if __name__ == "__main__":
    main()
