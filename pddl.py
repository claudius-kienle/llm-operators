"""
pddl_parser.py | Utilities related to PDDL.
"""
import copy
import re
from contextlib import contextmanager
import os
import json


def save_gt_and_learned_plans(
    curr_iteration, directory, dataset, gt_plans, solved_plans_pddl, problems
):
    plan_filename = os.path.join(directory, f"{dataset}_plans_it_{curr_iteration}.json")

    output_plans = {}
    for plan_id in solved_plans_pddl:
        output_plans[plan_id] = {
            "problem": problems[plan_id].goal_language,
            "solved_plan": str(solved_plans_pddl[plan_id]),
            "gt_plan": str(gt_plans[plan_id]),
        }
    with open(plan_filename, "w") as f:
        json.dump(output_plans, f)
    return plan_filename


def save_learned_operators(curr_iteration, directory, dataset, train_domain, gt_domain):
    operators_filename = os.path.join(
        directory, f"{dataset}_operators_it_{curr_iteration}.json"
    )

    output_operators = {}
    for operator_name in train_domain.operators:
        output_operators[operator_name] = {
            "operator_name": operator_name,
            "pddl_operator": str(train_domain.operators[operator_name]),
        }
    with open(operators_filename, "w") as f:
        json.dump(output_operators, f)
    return operators_filename


@contextmanager
def ablate_operator(domain, operator_name, contents="[insert]"):
    ablated_operator = domain.operators[operator_name]
    domain.operators[
        operator_name
    ] = f"""(:action {operator_name}
    {contents}
)"""
    yield domain
    domain.operators[operator_name] = ablated_operator
    print("restoring", operator_name)


class PDDLParser:
    @classmethod
    def _purge_comments(self, pddl_str):
        # Purge comments from the given string.
        while True:
            match = re.search(r";(.*)\n", pddl_str)
            if match is None:
                return pddl_str
            start, end = match.start(), match.end()
            pddl_str = pddl_str[:start] + pddl_str[end - 1 :]

    @classmethod
    def _parse_domain_operators(cls, pddl_domain):
        matches = re.finditer(r"\(:action", pddl_domain)
        operators = {}
        for match in matches:
            start_ind = match.start()
            op = cls._find_balanced_expression(pddl_domain, start_ind).strip()
            patt = r"\(:action(.*):parameters(.*):precondition(.*):effect(.*)\)"
            op_match = re.match(patt, op, re.DOTALL)
            op_name, params, preconds, effects = op_match.groups()
            op_name = op_name.strip()
            operators[op_name] = op
        return operators

    @classmethod
    def _find_labelled_expression(cls, string, label):
        # label like :action
        mat = re.search(r"\(" + label, string)
        if mat is None:
            return ""
        start_ind = mat.start()
        return cls._find_balanced_expression(string, start_ind)

    @staticmethod
    def _find_balanced_expression(string, index):
        """Find balanced expression in string starting from given index.
        """
        assert string[index] == "("
        start_index = index
        balance = 1
        while balance != 0:
            index += 1
            symbol = string[index]
            if symbol == "(":
                balance += 1
            elif symbol == ")":
                balance -= 1
        return string[start_index : index + 1]

    @staticmethod
    def _find_all_balanced_expressions(string):
        """Return a list of all balanced expressions in a string,
        starting from the beginning.
        """
        assert string[0] == "("
        assert string[-1] == ")"
        exprs = []
        index = 0
        start_index = index
        balance = 1
        while index < len(string) - 1:
            index += 1
            if balance == 0:
                exprs.append(string[start_index:index])
                # Jump to next "(".
                while True:
                    if string[index] == "(":
                        break
                    index += 1
                start_index = index
                balance = 1
                continue
            symbol = string[index]
            if symbol == "(":
                balance += 1
            elif symbol == ")":
                balance -= 1
        assert balance == 0
        exprs.append(string[start_index : index + 1])
        return exprs


class Domain:
    def __init__(
        self,
        pddl_domain=None,
        parent_domain=None,
        domain_name=None,
        requirements=None,
        constants=None,
        types=None,
        predicates=None,
        operators=None,
        functions=None,
    ):
        self.pddl_domain = pddl_domain
        self.parent_domain = parent_domain
        self.domain_name = self.init_domain_name(domain_name)
        self.requirements = self.init_simple_pddl(requirements, "requirements")
        self.constants = self.init_simple_pddl(predicates, "constants")
        self.types = self.init_simple_pddl(types, "types")
        self.predicates = self.init_simple_pddl(predicates, "predicates")
        self.functions = self.init_simple_pddl(functions, "functions")
        self.operators = self.init_operators(operators)

        self.ground_truth_operators = None

    def init_pddl_domain(self, pddl_domain):
        if pddl_domain is not None:
            pddl_domain = PDDLParser._purge_comments(pddl_domain)
        return pddl_domain

    def init_domain_name(self, domain_name):
        if domain_name is not None:
            return domain_name
        elif self.parent_domain is not None:
            return self.parent_domain.domain_name
        elif self.pddl_domain is not None:
            patt = r"\(domain(.*?)\)"
            return re.search(patt, self.pddl_domain).groups()[0].strip()
        else:
            return domain_name

    def init_simple_pddl(self, initial_value, str_keyword):
        if initial_value is not None:
            return initial_value
        elif self.parent_domain is not None:
            return vars(self.parent_domain)[str_keyword]
        elif self.pddl_domain is not None:
            try:
                return PDDLParser._find_labelled_expression(
                    self.pddl_domain, f":{str_keyword}"
                )
            except:
                return ""
        return initial_value

    def init_operators(self, initial_value):
        if initial_value is not None:
            return initial_value
        elif self.parent_domain is not None:
            return copy.deepcopy(
                vars(self.parent_domain)["operators"]
            )  # Don't share the operator object.
        elif self.pddl_domain is not None:
            return PDDLParser._parse_domain_operators(self.pddl_domain)
        return initial_value

    def add_operator(self, operator_name, operator_pddl):
        self.operators[operator_name] = operator_pddl

    def remove_operator(self, operator_name):
        del self.operators[operator_name]

    def init_requirements(self, requirements):
        return PDDLParser._find_labelled_expression(self.pddl_domain, ":requirements")

    def operators_to_string(self, separator="\n"):
        return separator.join([f"""{s}""" for _, s in self.operators.items()])

    def to_string(self):
        if self.pddl_domain is not None:
            return self.pddl_domain
        else:

            return f"""
            (define (domain {self.domain_name})
                {self.requirements}
                {self.types}
                {self.predicates}
                {self.functions}
                {self.operators_to_string()}
            )
            """

    def domain_definition_to_string(self):
        return "\n".join(
            [self.requirements, self.types, self.predicates, self.functions]
        )


class PDDLPlan:
    PDDL_ACTION = "action"
    PDDL_ARGUMENTS = "args"
    PDDL_INFINITE_COST = 100000

    def __init__(
        self, plan=None, plan_string=None, overall_plan_cost=PDDL_INFINITE_COST
    ):
        self.plan = plan
        self.plan_string = plan_string
        if self.plan is None and self.plan_string:
            self.plan = self.string_to_plan(self.plan_string)
        if self.plan_string is None and self.plan:
            self.plan_string = self.plan_to_string(self.plan)

        self.overall_plan_cost = overall_plan_cost

    def plan_to_string(self, plan):
        return "\n".join(
            [
                f"({a[PDDLPlan.PDDL_ACTION]} {' '.join(a[PDDLPlan.PDDL_ARGUMENTS])})"
                for a in self.plan
            ]
        )

    def string_to_plan(self, plan_string):
        action_strings = plan_string.strip().split("\n")
        actions = []
        for a in action_strings:
            assert a.startswith("(") and a.endswith(")")
            tokens = a.strip("()").split(" ")
            assert len(tokens) > 0
            actions.append(
                {PDDLPlan.PDDL_ACTION: tokens[0], PDDLPlan.PDDL_ARGUMENTS: tokens[1:]}
            )
        return actions


class PDDLProblem:
    def __init__(self, ground_truth_pddl_problem_string=None):
        self.ground_truth_pddl_problem_string = ground_truth_pddl_problem_string
        self.ground_truth_goal = self.parse_goal_pddl(
            self.ground_truth_pddl_problem_string
        )

    def get_pddl_string_with_proposed_goal(self, proposed_goal):
        # Replaces the ground truth goal with a proposed goal.
        pddl_string = self.ground_truth_pddl_problem_string.replace(
            self.ground_truth_goal, proposed_goal
        )
        return pddl_string

    def parse_goal_pddl(self, pddl_problem):
        pddl_problem = PDDLParser._purge_comments(pddl_problem)
        return PDDLParser._find_labelled_expression(pddl_problem, ":goal")

