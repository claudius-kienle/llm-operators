"""
planning_domain.py | Classes for representing a planning domain.
"""


class Problem:
    # A planning problem.
    def __init__(
        self,
        problem_id=None,
        language=None,
        pddl_problem=None,
        pddl_plan=None,
        low_level_plan=None,
    ):
        self.problem_id = problem_id
        self.language = language  # A string describing the planning problem.
        self.pddl_problem = pddl_problem  # A structured PDDLgym object.
        self.pddl_plan = pddl_plan
        self.low_level_plan = low_level_plan

        self.proposed_pddl_plan = []

    def to_string(self):
        if self.pddl_problem is not None:
            return str(self.pddl_problem)
        else:
            assert False
