
import matplotlib.pyplot as plt
from sys import argv
import solutions
import load_graphs
from checker import check
import numpy as np

def count_num_edges(adj_matrix: list[list[bool]]) -> int:
    ans = 0
    for v in adj_matrix:
        for vv in v:
            if vv:
                ans += 1
    return int(ans / 2)

def load_results(problem_source, solution_source):
    graphs = load_graphs.load_adjacency_matrixes(problem_source)

    lines = [line.strip() for line in open(solution_source, "r")]
    current_line = 0

    results_by_num_edges = {}
    for adj_matrix, num_components in graphs:

        num_edges = count_num_edges(adj_matrix)
        if not num_edges in results_by_num_edges:
            results_by_num_edges[num_edges] = [0, []]

        parts = lines[current_line].split(' ')
        current_line += 1

        result = int(parts[0])
        
        if result == solutions.INFEASIBLE:
            time = float(parts[1])
            results_by_num_edges[num_edges][1].append(time)
        elif result == solutions.FEASIBLE:
            result_edges = int(parts[1])
            edges = []
            for _ in range(result_edges):
                parts = lines[current_line].split(' ')
                current_line += 1

                f, t = int(parts[0]), int(parts[1])
                edges.append((f, t))

            assert(check(adj_matrix, edges, num_components))

            results_by_num_edges[num_edges][0] += 1

        elif result == solutions.OPTIMAL:
            result_edges = int(parts[1])
            time = float(parts[2])

            edges = []
            for _ in range(result_edges):
                parts = lines[current_line].split(' ')
                current_line += 1

                f, t = int(parts[0]), int(parts[1])
                edges.append((f, t))
            
            assert(check(adj_matrix, edges, num_components))

            results_by_num_edges[num_edges][1].append(time)
        elif result == solutions.UNKNOWN:
            results_by_num_edges[num_edges][0] += 1
    
    return results_by_num_edges


def plot_results(results_by_num_edges, filename: str) -> None:
    num_edges = sorted(results_by_num_edges.keys())
    
    # Calculate average and standard deviation
    averages = []
    std_devs = []
    timeouts = []
    
    for edges in num_edges:
        times = results_by_num_edges[edges][1]
        if times:
            averages.append(np.mean(times))
            std_devs.append(np.std(times))
        else:
            averages.append(4)
            std_devs.append(0)
        timeouts.append(results_by_num_edges[edges][0])
    
    # Create subplots
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    
    # Plot average times
    axs[0].plot(num_edges, averages, marker='o', label='Average Time')
    axs[0].set_xlabel('Number of Edges')
    axs[0].set_ylabel('Average Time (s)')
    axs[0].set_title('Average Time vs Number of Edges')
    axs[0].grid(True)
    
    # Plot standard deviation
    axs[1].plot(num_edges, std_devs, marker='o', label='Standard Deviation')
    axs[1].set_xlabel('Number of Edges')
    axs[1].set_ylabel('Standard Deviation (s)')
    axs[1].set_title('Standard Deviation vs Number of Edges')
    axs[1].grid(True)
    
    # Plot number of timeouts
    axs[2].plot(num_edges, timeouts, marker='o', label='Number of Timeouts')
    axs[2].set_xlabel('Number of Edges')
    axs[2].set_ylabel('Number of Timeouts')
    axs[2].set_title('Number of Timeouts vs Number of Edges')
    axs[2].grid(True)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(filename)
    plt.show()


def main():
    results = load_results(argv[1], argv[2])
    plot_results(results, argv[3])


if __name__ == "__main__":
    main()
