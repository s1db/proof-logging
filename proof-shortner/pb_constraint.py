from typing import Iterable, Dict
from collections import defaultdict
import copy
from math import ceil


class PBConstraint:
    def __init__(self, literals, coefficients, degree):
        self.literals = set(literals)
        self.coefficients = defaultdict(int)
        self.degree = degree  # of falsity
        self.no_of_literals = len(self.literals)
        for literal, coefficient in zip(literals, coefficients):
            self.coefficients[literal] += coefficient
        if self.no_of_literals != len(self.coefficients):
            raise Exception("unequal number of literals and coefficients.")

    def is_unsatisfied(self, assignment: Iterable) -> bool:
        """
        :param: assignment: the assignment
        :return: True if the constraint is satisfied in the `assignment`, i.e. one of its literals is True.
        """
        return self.slack(assignment) < 0

    def coefficient_normalized_form(self):
        for i in self.literals:
            coefficient = self.coefficients[i]
            if coefficient < 0:
                # update degree
                self.degree = self.degree - coefficient
                # update coefficient dict
                self.coefficients[-i] = -coefficient
                del self.coefficients[i]
                # update literals set
                self.literals.add(-i)
                self.literals.remove(i)

    def slack(self, assignment: Iterable) -> int:
        """
        :param: assignment: the assignment
        :return: the slack of the constraint in the `assignment`, i.e. the number of literals not falsified by an assignment minus the degree.
        """
        temp = 0
        for i in self.literals:
            if -i not in assignment:
                temp += self.coefficients[i]
        temp -= self.degree
        return temp

    def propagate(self, assignment: Iterable) -> Iterable:
        """
        :param: assignment: the assignment
        :return: the literals that need be added to the assignment to satisfy the constraint.
        """

        need_to_be_true = []
        slack = self.slack(assignment)
        for i in self.literals:
            # if any assignment is falsified, skip it.
            if -i not in assignment:
                if self.coefficients[i] > slack:
                    need_to_be_true.append(i)
        return need_to_be_true

    def negation(self):
        for i in self.literals:
            self.coefficients[i] = - self.coefficients[i]
        self.degree = -self.degree + 1
        self.coefficient_normalized_form()

    def implies(self, constraint):
        """
        TODO: check if self semantically implies other constraint
        :param: constraint 
        :return: True if self semantically implies other constraint
        """
        weaken_cost = 0
        for i in constraint.literals:
            if i not in self.literals:
                return False
            else:
                if self.coefficients[i] < constraint.coefficients[i]:
                    return False
                else:
                    weaken_cost += self.coefficients[i] - \
                        constraint.coefficients[i]
        if self.degree < constraint.degree:
            return False
        else:
            weaken_cost += self.degree - constraint.degree
        return weaken_cost

    def saturation(self):
        for i in self.literals:
            self.coefficients[i] = min(self.coefficients[i], self.degree)

    @staticmethod
    def multiply(constraint, constant):
        for i in constraint.literals:
            constraint.coefficients[i] = constraint.coefficients[i] * constant
        constraint.degree = constraint.degree * constant
        constraint.coefficient_normalized_form()

    @staticmethod
    def add(constraint1, constraint2):
        new_constraint = copy.deepcopy(constraint1)
        for i in constraint2.literals:
            new_constraint.coefficients[i] += constraint2.coefficients[i]
        new_constraint.degree += constraint2.degree
        new_constraint.coefficient_normalized_form()
        return new_constraint

    @staticmethod
    def subtract(constraint1, constraint2):
        new_constraint = copy.deepcopy(constraint1)
        for i in constraint2.literals:
            new_constraint.coefficients[i] -= constraint2.coefficients[i]
        new_constraint.degree -= constraint2.degree
        new_constraint.coefficient_normalized_form()
        return new_constraint

    @staticmethod
    def divide(constraint1, constant):
        new_constraint = copy.deepcopy(constraint1)
        for i in new_constraint.literals:
            new_constraint.coefficients[i] = ceil(
                new_constraint.coefficients[i] / constant)
        new_constraint.degree = ceil(new_constraint.degree / constant)
        new_constraint.coefficient_normalized_form()
        return new_constraint

    def __str__(self) -> str:
        #  dictionary to string keys and values space seprated
        temp = ""
        for i in self.literals:
            if i > 0:
                temp += str(self.coefficients[i]) + " x" + str(i) + " + "
            else:
                temp += str(self.coefficients[i]) + " ~x" + str(-i) + " + "
        temp = temp[:-3] + " >= " + str(self.degree)
        return temp


class PBModel:
    def __init__(self, filename):
        self.filename = filename
        self.constraint_db: Dict[str, PBConstraint] = {}
        self.no_of_variables = 0
        self.no_of_constraints = 0
        self.parse()

    def add_constraint(self, constraint: PBConstraint):
        self.no_of_constraints += 1
        self.constraint_db[self.no_of_constraints] = constraint
        print("constraint "+str(self.no_of_constraints)+" added: ", constraint)

    def constraint_parser(self, line: str) -> PBConstraint:
        line = line[:-1].split(">=")
        degree = int(line[1])
        line = line[0].split()
        coefficients = [int(line[i])
                        for i in range(0, len(line), 2)]
        literals = [int(line[i][1:]) if line[i][0] != "~" else -
                    1*int(line[i][2:]) for i in range(1, len(line), 2)]
        if len(coefficients) != len(literals):
            raise Exception(
                "unequal number of literals and coefficients")
        temp = PBConstraint(literals, coefficients, degree)
        self.no_of_variables += len(literals)
        return temp

    def parse(self) -> None:
        with open(self.filename, "r") as f:
            for line in f:

                line = line.strip()
                if not line.startswith("*") and len(line) > 0:
                    temp = self.constraint_parser(line)
                    self.add_constraint(temp)
        print("MODEL PARSED -- NO OF CONSTRAINTS: ", self.no_of_constraints)

    def admit_pol_step(self, statement: str) -> None:
        statement = statement.split(" ")[1:-1]
        stack = []
        operations = ["+", "-", "*", "/"]
        if len(statement) == 1:
            temp = copy.deepcopy(self.constraint_db[int(statement[0])])
            stack.append(temp)
        for i in statement:
            if i not in operations:
                temp = copy.deepcopy(self.constraint_db[int(i)])
                stack.append(temp)
            else:
                a = stack.pop()
                b = stack.pop()
                temp = None
                if i == '+':
                    temp = PBConstraint.add(a, b)
                if i == '-':
                    temp = PBConstraint.subtract(a, b)
                if i == '*':
                    raise NotImplementedError("multiplication is not yet implemented")
                    # temp = PBConstraint.multiply(self.constraint_db[a], b)
                if i == '/':
                    raise NotImplementedError("division is not yet implemented")
                    # temp = PBConstraint.divide(self.constraint_db[a], b)
                stack.append(temp)
        self.add_constraint(stack.pop())

    def admit_j_step(self, line: str) -> None:
        # constraint = self.constraint_parser(line[1:-1])
        line = line[:-1].split(">=")
        degree = int(line[1][:-1])
        line = line[0].split()[2:]
        coefficients = [int(line[i])
                        for i in range(0, len(line), 2)]
        literals = [int(line[i][1:]) if line[i][0] != "~" else -
                    1*int(line[i][2:]) for i in range(1, len(line), 2)]
        if len(coefficients) != len(literals):
            raise Exception(
                "unequal number of literals and coefficients")
        temp = PBConstraint(literals, coefficients, degree)
        self.add_constraint(temp)

    def admit_rup_step(self, line: str) -> None:
        print("RUP STEP: ", line[:-1])
        constraint = self.constraint_parser(line[1:-1])
        constraint.negation()
        if not self.rup(constraint):
            print("    RUP Failed -- cannot add constraint")
            raise Exception("RUP Failed -- Refutation Failed.")
        print("    RUP Succeeded")
        constraint.negation()
        self.add_constraint(constraint)

    def rup(self, constraint: PBConstraint) -> bool:
        tau = constraint.propagate([])
        print("    ASSIGNMENT: ", tau)
        while True:
            unit_propagated = False
            for c in self.constraint_db:
                if self.constraint_db[c].is_unsatisfied(tau):
                    return True
            for c in self.constraint_db:
                c_propagates = self.constraint_db[c].propagate(tau)
                if c_propagates != []:
                    tau.append(c_propagates)
                    unit_propagated = True
                    break
            if not unit_propagated:
                return False

    def admit_check_contradiction(self, line: str) -> None:
        id = int(line.split()[1])
        if self.constraint_db[id].is_unsatisfied([]):
            print("Contradiction Found")
        else:
            print("Incorrect Contradiction Claimed")


class PBProof:
    def __init__(self, model_file, proof_file):
        self.proof_file = proof_file
        self.model = PBModel(model_file)
        self.no_of_formulas = self.model.no_of_constraints
        self.parse()

    def parse(self):
        with open(self.proof_file, "r") as f:
            for line in f:
                if line[0] == '#':
                    print("COMMENT: ", line[:-1])
                    pass
                elif line.startswith("pseudo"):
                    print("FILE TYPE: ", line)
                elif line[0] == 'f':
                    print("FORMULA CHECK: ", line)
                    f = int(line.split()[1])
                    if type(f) == int:
                        if f != self.no_of_formulas:
                            raise Exception("Number of formulas mismatch")
                elif line[0] == 'p':
                    self.model.admit_pol_step(line)
                elif line[0] == 'u':
                    self.model.admit_rup_step(line)
                elif line[0] == 'j':
                    self.model.admit_j_step(line)
                elif line[0] == 'c':
                    self.model.admit_check_contradiction(line)


if "__main__" == __name__:
    # proof = PBProof('proof-shortner/proofs/rup_php65.opb', 'proof-shortner/proofs/rup_php65.pbp')
    # proof = PBProof('proof-shortner/proofs/rup_fail.opb', 'proof-shortner/proofs/rup_fail.pbp')
    proof = PBProof('proof-shortner/proofs/proof.opb',
                    'proof-shortner/proofs/proof.pbp')
