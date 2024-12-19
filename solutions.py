
INFEASIBLE = 0
OPTIMAL = 1
FEASIBLE = 2
UNKNOWN = 3

class Solution:
    def __init__(self, status: int, solution: list[tuple[int, int]] | None, time: float):
        self.status = status
        self.solution = solution
        self.time = time

    def log(self, file):
        if self.solution is None:
            file.write(f"{self.status} {self.time}\n")
        else:
            file.write(f"{self.status} {len(self.solution)} {self.time}\n")
            for f, t in self.solution:
                file.write(f"{f} {t}\n")
                