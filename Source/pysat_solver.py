from pysat.solvers import Solver

class PySATSolver:
    def __init__(self, cnf):
        self.cnf = cnf

    def solve(self, solver_name="g3"):
        solver = Solver(name=solver_name)
        for clause in self.cnf:
            solver.add_clause(clause)
        if solver.solve():
            return solver.get_model()
        return None
