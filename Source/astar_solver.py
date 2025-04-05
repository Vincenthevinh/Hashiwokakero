import heapq
from collections import defaultdict

class AStarSolver:
    def __init__(self, cnf):
        self.cnf = cnf
        self.variables = self._extract_variables()
        self.freq = self._compute_frequency()

    def _extract_variables(self):
        variables = set()
        for clause in self.cnf:
            for lit in clause:
                variables.add(abs(lit))
        return variables

    def _compute_frequency(self):
        freq = defaultdict(int)
        for clause in self.cnf:
            for lit in clause:
                freq[abs(lit)] += 1
        return freq

    def solve(self):
        # Mỗi phần tử trong heap: (f, g, counter, current_assignment, unsat)
        heap = []
        counter = 0
        initial_assignment = {}
        initial_unsat = set(range(len(self.cnf)))
        heapq.heappush(heap, (len(initial_unsat), 0, counter, initial_assignment, initial_unsat))
        counter += 1

        visited = set()

        while heap:
            current_f, current_g, _, current_assignment, unsat = heapq.heappop(heap)

            if not unsat:
                return self._format_solution(current_assignment)

            assignment_key = frozenset(current_assignment.items())
            if assignment_key in visited:
                continue
            visited.add(assignment_key)

            # Unit propagation
            unit_clauses = []
            for clause_idx in unsat:
                clause = self.cnf[clause_idx]
                unassigned_lits = [lit for lit in clause if abs(lit) not in current_assignment]
                if len(unassigned_lits) == 1:
                    lit = unassigned_lits[0]
                    var = abs(lit)
                    value = (lit > 0)
                    unit_clauses.append((var, value))

            if unit_clauses:
                new_assignment = current_assignment.copy()
                new_unsat = unsat.copy()
                for var, value in unit_clauses:
                    new_assignment[var] = value
                    # loại bỏ các clause được thỏa
                    for c_idx in list(new_unsat):
                        cl = self.cnf[c_idx]
                        for l in cl:
                            if (l > 0 and new_assignment.get(abs(l), False)) or \
                               (l < 0 and not new_assignment.get(abs(l), True)):
                                new_unsat.remove(c_idx)
                                break
                heapq.heappush(heap, (len(new_unsat), current_g + len(unit_clauses), counter, new_assignment, new_unsat))
                counter += 1
                continue

            # Heuristic chọn biến
            var_scores = defaultdict(float)
            bridge_vars = set()

            # Ví dụ: tăng trọng số cho biến có tần suất cao
            for clause_idx in unsat:
                clause = self.cnf[clause_idx]
                if any(abs(lit) in self.freq and self.freq[abs(lit)] > 5 for lit in clause):
                    for lit in clause:
                        var = abs(lit)
                        if var not in current_assignment:
                            var_scores[var] += 2.0
                            bridge_vars.add(var)

            if not var_scores:
                # Fallback
                for clause_idx in unsat:
                    clause = self.cnf[clause_idx]
                    for lit in clause:
                        var = abs(lit)
                        if var not in current_assignment:
                            var_scores[var] += 1.0 / len(clause)

            if not var_scores:
                # Không còn biến nào để gán => bế tắc
                continue

            next_var = max(var_scores.keys(), key=lambda x: var_scores[x])

            # Thử gán True hoặc False
            for value in [True, False]:
                new_assignment = current_assignment.copy()
                new_assignment[next_var] = value
                new_unsat = set()
                for c_idx in unsat:
                    cl = self.cnf[c_idx]
                    satisfied = False
                    for l in cl:
                        if abs(l) in new_assignment:
                            if (l > 0 and new_assignment[abs(l)]) or \
                               (l < 0 and not new_assignment[abs(l)]):
                                satisfied = True
                                break
                    if not satisfied:
                        new_unsat.add(c_idx)

                cost = current_g + 1
                # Ưu tiên biến 'bridge' (nếu muốn)
                if next_var in bridge_vars:
                    f_val = len(new_unsat)
                else:
                    f_val = len(new_unsat) + cost

                heapq.heappush(heap, (f_val, cost, counter, new_assignment, new_unsat))
                counter += 1

        return None

    def _format_solution(self, assignment):
        solution = []
        for var in sorted(assignment.keys()):
            if assignment[var]:
                solution.append(var)
            else:
                solution.append(-var)
        return solution
