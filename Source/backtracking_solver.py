from collections import defaultdict

class BacktrackingSolver:
    def __init__(self, cnf):
        self.cnf = cnf
        self.variables = self._extract_variables()
        self.freq = self._compute_frequency()

    def _extract_variables(self):
        variables = set()
        for clause in self.cnf:
            for lit in clause:
                variables.add(abs(lit))
        return sorted(variables)

    def _compute_frequency(self):
        freq = defaultdict(int)
        for clause in self.cnf:
            for lit in clause:
                freq[abs(lit)] += 1
        return freq

    def solve(self):
        assignment = {}
        unsat = set(range(len(self.cnf)))
        assignment, unsat = self.unit_propagate(assignment, unsat)
        if assignment is None:
            return None, 0

        solution = self.backtrack(assignment, unsat)
        return solution

    def unit_propagate(self, assignment, unsat):
        new_assignment = assignment.copy()
        new_unsat = unsat.copy()

        while True:
            unit_clause_found = False
            for clause_idx in list(new_unsat):
                clause = self.cnf[clause_idx]
                unassigned = [lit for lit in clause if abs(lit) not in new_assignment]
                if len(unassigned) == 0:
                    if not any((lit > 0 and new_assignment.get(abs(lit), False)) or
                            (lit < 0 and not new_assignment.get(abs(lit), True)) for lit in clause):
                        return None, None  # conflict
                elif len(unassigned) == 1:
                    unit_clause_found = True
                    lit = unassigned[0]
                    var = abs(lit)
                    val = lit > 0
                    new_assignment[var] = val

                    new_unsat = {idx for idx in new_unsat if not any(
                        (l > 0 and new_assignment.get(abs(l), False)) or
                        (l < 0 and not new_assignment.get(abs(l), True)) for l in self.cnf[idx]
                    )}
                    break  # Re-evaluate from beginning after update
            if not unit_clause_found:
                break
        return new_assignment, new_unsat


    def backtrack(self, assignment, unsat):
        if not unsat:
            return self._format_solution(assignment)

        var = self.select_unassigned_variable(assignment, unsat)
        if var is None:
            return None

        for value in [True, False]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            new_unsat = set()
            for c_idx in unsat:
                cl = self.cnf[c_idx]
                if not any((lit > 0 and new_assignment.get(abs(lit), False)) or 
                           (lit < 0 and not new_assignment.get(abs(lit), True)) for lit in cl):
                    new_unsat.add(c_idx)

            propagated_assignment, propagated_unsat = self.unit_propagate(new_assignment, new_unsat)
            if propagated_assignment is not None:
                result = self.backtrack(propagated_assignment, propagated_unsat)
                if result:
                    return result

        return None

    def select_unassigned_variable(self, assignment, unsat):
        var_scores = defaultdict(float)
        bridge_vars = set()

        for clause_idx in unsat:
            clause = self.cnf[clause_idx]
            if any(abs(lit) in self.freq and self.freq[abs(lit)] > 5 for lit in clause):
                for lit in clause:
                    var = abs(lit)
                    if var not in assignment:
                        var_scores[var] += 2.0
                        bridge_vars.add(var)

        if not var_scores:
            for clause_idx in unsat:
                clause = self.cnf[clause_idx]
                for lit in clause:
                    var = abs(lit)
                    if var not in assignment:
                        var_scores[var] += 1.0 / len(clause)

        if not var_scores:
            return None

        return max(var_scores.keys(), key=lambda x: var_scores[x])

    def _format_solution(self, assignment):
        solution = []
        for var in sorted(assignment.keys()):
            if assignment[var]:
                solution.append(var)
            else:
                solution.append(-var)
        return solution
