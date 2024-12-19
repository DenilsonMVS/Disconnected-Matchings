
def check(graph: list[list[bool]], matching: list[(int, int)], num_components: int):
    n = len(graph)


    adj_list = [[] for _ in range(n)]

    for f, t in matching:
        if not graph[f][t]:
            print(f"{f} {t} não existe no grafo original")
            return False

        adj_list[f].append(t)
        adj_list[t].append(f)
    
    for i in range(n):
        node = adj_list[i]
        if len(node) >= 2:
            print(f"node {i} have degree {len(node)}")
            return False
    

    induced_graph = [[] for _ in range(n)]

    for i in range(n):
        node = adj_list[i]
        if len(node) == 1:
            for j in range(n):
                if graph[i][j]:
                    induced_graph[i].append(j)


    color = [-1 for _ in range(n)]

    for i in range(n):
        if color[i] != -1 or len(adj_list[i]) == 0:
            continue

        stack = []
        stack.append(i)
        while len(stack):
            cur = stack.pop()
            if color[cur] != -1:
                continue

            color[cur] = i

            for to in induced_graph[cur]:
                stack.append(to)
    
    colors = set(color)
    if -1 in colors:
        colors.remove(-1)

    if len(colors) < num_components:
        print(f"Número de componentes: {len(colors)}/{num_components}")
        return False

    return True
