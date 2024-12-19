from os import system
from random import shuffle
import tests


class Graph:
    def __init__(self, num_vertices: int, edges: list[(int, int)]):
        self.num_vertices = num_vertices
        self.edges = edges
    
    def log(self, file, num_components):
        file.write(f"{self.num_vertices} {len(self.edges)} {num_components}\n")
        for edge in self.edges:
            file.write(f"{edge[0]} {edge[1]}\n")

    def gen_random_graph(num_vertices: int, num_edges: int):
        edges = []
        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                edges.append((i, j))

        shuffle(edges)

        return Graph(num_vertices, edges[0:num_edges])


def gen_graphs(num_vertices: int, components: list[int]):
    total_num_edges = num_vertices * (num_vertices - 1) / 2
    graphs = []
    for step in tests.edge_steps:
        num_edges = int(total_num_edges * step)
        for _ in range(tests.random_instances_per_case):
            graphs.append(Graph.gen_random_graph(num_vertices, num_edges))
    
    for num_components in components:
        file = open(f"test_instances/{num_vertices}_{num_components}.txt", "w")
        file.write(f"{len(graphs)}\n")
        for graph in graphs:
            graph.log(file, num_components)
    

def main():
    for num_vertices, components in tests.config:
        gen_graphs(num_vertices, components)

if __name__ == "__main__":
    main()
