import copy
import re
from contextlib import contextmanager


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


class DomainParser:
    def __init__(self, domain_fname):

        self.domain_fname = domain_fname

        # Read files.
        with open(domain_fname, "r") as f:
            self.domain = f.read().lower()

        self.domain = self._purge_comments(self.domain)
        assert ";" not in self.domain

        self._parse_domain()

    @classmethod
    def _purge_comments(self, pddl_str):
        # Purge comments from the given string.
        while True:
            match = re.search(r";(.*)\n", pddl_str)
            if match is None:
                return pddl_str
            start, end = match.start(), match.end()
            pddl_str = pddl_str[:start] + pddl_str[end - 1 :]

    def to_string(self):
        operator_string = "\n".join(
            [
                f"""
{s}"""
                for _, s in self.operators.items()
            ]
        )
        return f"""
(define (domain {self.domain_name})
    {self.requirements}
    {self.types}
    {self.predicates}
    {self.constants}
    {operator_string}
)
"""

    def _parse_domain(self):
        patt = r"\(domain(.*?)\)"
        self.domain_name = re.search(patt, self.domain).groups()[0].strip()
        self._parse_domain_requirements()
        self._parse_domain_types()
        self._parse_domain_predicates()
        self._parse_domain_constants()
        self.operators = self._parse_domain_operators(self.domain)

    def _parse_domain_requirements(self):
        self.requirements = self._find_labelled_expression(self.domain, ":requirements")

    def _parse_domain_types(self):
        self.types = self._find_labelled_expression(self.domain, ":types")

    def _parse_domain_predicates(self):
        self.predicates = self._find_labelled_expression(self.domain, ":predicates")

    def _parse_domain_constants(self):
        self.constants = self._find_labelled_expression(self.domain, ":constants")

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
        types=None,
        predicates=None,
        operators=None,
    ):
        self.pddl_domain = pddl_domain
        self.parent_domain = parent_domain
        self.domain_name = self.init_domain_name(domain_name)
        self.requirements = self.init_simple_pddl(requirements, "requirements")
        self.types = self.init_simple_pddl(types, "types")
        self.predicates = self.init_simple_pddl(predicates, "predicates")
        self.operators = self.init_operators(operators)

    def init_pddl_domain(self, pddl_domain):
        if pddl_domain is not None:
            pddl_domain = DomainParser._purge_comments(pddl_domain)
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
            return DomainParser._find_labelled_expression(
                self.pddl_domain, f":{str_keyword}"
            )
        return initial_value

    def init_operators(self, initial_value):
        if initial_value is not None:
            return initial_value
        elif self.parent_domain is not None:
            return copy.deepcopy(
                vars(self.parent_domain)["operators"]
            )  # Don't share the operator object.
        elif self.pddl_domain is not None:
            return DomainParser._parse_domain_operators(self.pddl_domain)
        return initial_value

    def init_requirements(self, requirements):
        return DomainParser._find_labelled_expression(self.pddl_domain, ":requirements")

    def to_string(self):
        if self.pddl_domain is not None:
            return self.pddl_domain
        else:
            assert False


class Problem:
    def __init__(
        self,
        pddl_problem=None,
        goal_str=None,
        initial_conditions_str=None,
        goal_language=None,
    ):
        self.goal_language = None
        self.pddl_problem = pddl_problem
        self.goal_str = goal_str
        if self.goal_str is None and not self.pddl_problem is None:
            self.goal_str = self.parse_goal_pddl(pddl_problem)

        self.initial_conditions_str = initial_conditions_str
        if self.initial_conditions_str is None and not self.pddl_problem is None:
            self.initial_condition_str = self.parse_initial_conditions_pddl(
                pddl_problem
            )

    def to_string(self):
        if self.pddl_problem is not None:
            return self.pddl_problem
        else:
            assert False

    def parse_goal_pddl(self, pddl_problem):
        pddl_problem = DomainParser._purge_comments(pddl_problem)
        return DomainParser._find_labelled_expression(pddl_problem, ":goal")

    def parse_initial_conditions_pddl(self, pddl_problem):
        pddl_problem = DomainParser._purge_comments(pddl_problem)
        return DomainParser._find_labelled_expression(pddl_problem, ":init")
