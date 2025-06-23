
def load_adjacency_matrixes(filename: str) -> list[tuple[list[list[bool]], int]]:
    lines = []
    file = open(filename)
    for line in file:
        lines.append(line)
        if line[-1] == "\n":
            lines[-1] = line[:-1]

    current_line = 0
    
    num_cases = int(lines[current_line])
    current_line += 1

    graphs = []
    for _ in range(num_cases):
        parts = lines[current_line].split(" ")
        current_line += 1

        num_vertices, num_edges, num_components = int(parts[0]), int(parts[1]), int(parts[2])

        graph = [[False for _ in range(num_vertices)] for _ in range(num_vertices)]

        for _ in range(num_edges):
            parts = lines[current_line].split(" ")
            current_line += 1

            f, t = int(parts[0]), int(parts[1])

            graph[f][t] = True
            graph[t][f] = True

        graphs.append((graph, num_components))

    return graphs
