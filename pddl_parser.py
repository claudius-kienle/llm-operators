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
        self._parse_domain_operators()

    def _parse_domain_requirements(self):
        self.requirements = self._find_labelled_expression(self.domain, ":requirements")

    def _parse_domain_types(self):
        self.types = self._find_labelled_expression(self.domain, ":types")

    def _parse_domain_predicates(self):
        self.predicates = self._find_labelled_expression(self.domain, ":predicates")

    def _parse_domain_constants(self):
        self.constants = self._find_labelled_expression(self.domain, ":constants")

    def _parse_domain_operators(self):
        matches = re.finditer(r"\(:action", self.domain)
        self.operators = {}
        for match in matches:
            start_ind = match.start()
            op = self._find_balanced_expression(self.domain, start_ind).strip()
            patt = r"\(:action(.*):parameters(.*):precondition(.*):effect(.*)\)"
            op_match = re.match(patt, op, re.DOTALL)
            op_name, params, preconds, effects = op_match.groups()
            op_name = op_name.strip()
            # params = params.strip()[1:-1].split("?")
            # if self.uses_typing:
            #     params = [(param.strip().split("-", 1)[0].strip(),
            #                param.strip().split("-", 1)[1].strip())
            #               for param in params[1:]]
            #     params = [self.types[v]("?"+k) for k, v in params]
            # else:
            #     params = [param.strip() for param in params[1:]]
            #     params = [self.types["default"]("?"+k) for k in params]
            # preconds = self._parse_into_literal(preconds.strip(), params + self.constants)
            # effects = self._parse_into_literal(effects.strip(), params + self.constants,
            #     is_effect=True)
            # self.operators[op_name] = Operator(
            #     op_name, params, preconds, effects)
            self.operators[op_name] = op

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
