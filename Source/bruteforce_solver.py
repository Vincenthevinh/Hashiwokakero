import time
import itertools
from collections import defaultdict
from hashiwokakero_cnf import HashiwokakeroCNF

class BruteForceSolver:
    def __init__(self, cnf):
        self.cnf = cnf
        self.variables = sorted(set(abs(lit) for clause in self.cnf for lit in clause))
        self.var_to_clauses = defaultdict(list)
        for i, clause in enumerate(self.cnf):
            for lit in clause:
                self.var_to_clauses[abs(lit)].append(i)
        
        self.cnf.sort(key=len)

    def solve(self, max_attempts=None, max_time=300):
        start_time = time.time()
        attempts = 0
        num_vars = len(self.variables)
        
        total_combinations = 2 ** num_vars
        
        chunk_size = min(100000, total_combinations)
        
        for values in itertools.product([0, 1], repeat=num_vars):
            # Kiểm tra giới hạn thời gian
            if time.time() - start_time > max_time:
                return None, (time.time() - start_time) * 1000
            
            attempts += 1
            if max_attempts and attempts > max_attempts:
                return None, (time.time() - start_time) * 1000
            
            # Chuyển đổi assignment từ binary (0, 1) sang dạng phù hợp cho CNF
            assignment = {var: val for var, val in zip(self.variables, values)}
            
            if self._is_satisfiable(assignment):
                solution = self._format_solution(assignment)
                return solution
        
        return None

    def _is_satisfiable(self, assignment):
        for clause in self.cnf:
            if not self._clause_satisfied(clause, assignment):
                return False
        return True
    
    def _clause_satisfied(self, clause, assignment):
        for lit in clause:
            var = abs(lit)
            val = assignment[var]
            
            # Kiểm tra nếu literal thỏa mãn
            if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                return True
        return False

    def _format_solution(self, assignment):
        solution = []
        for var in self.variables:
            if assignment[var] == 1:
                solution.append(var)
            else:
                solution.append(-var)
        return solution
    
    def pre_process(self):
        unit_clauses = [clause[0] for clause in self.cnf if len(clause) == 1]
        
        # Xác định biến chỉ xuất hiện dạng dương hoặc âm
        pos_vars = set()
        neg_vars = set()
        
        for var in self.variables:
            pos_count = sum(1 for clause in self.cnf if var in clause)
            neg_count = sum(1 for clause in self.cnf if -var in clause)
            
            if pos_count > 0 and neg_count == 0:
                pos_vars.add(var)
            elif neg_count > 0 and pos_count == 0:
                neg_vars.add(var)
        
        return unit_clauses, pos_vars, neg_vars

def main():
    grid = [
        [2, 0, 2, 0],
        [0, 0, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 1, 0],
    ]
    hashi_cnf = HashiwokakeroCNF(grid)
    cnf = hashi_cnf.get_cnf()
    
    solver = BruteForceSolver(cnf)
    solver.pre_process()
    
    solution, duration = solver.solve()
    
    if solution:
        print(f"Solution found in {duration:.4f} ms:")
        print(solution)
    else:
        print(f"No solution found. Time: {duration:.4f} ms")

if __name__ == "__main__":
    main()