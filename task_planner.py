"""
task_planner.py 
Utilities for generating task level plans.
"""
from pddlgym_planners.fd import FD
from pddlgym_planners.planner import PlanningFailure, PlanningTimeout
from tempfile import NamedTemporaryFile

TASK_PLANNER_FD = "task_planner_fd"


def evaluate_task_plans_and_costs_for_problems(pddl_domain, problems, verbose=False):
    """
    Runs task planner to evaluate task plans for a set of planning problems, given a PDDL domain.
    :ret: problems updated with PDDL plans.
    """
    for problem in problems:
        evaluate_task_plans_and_costs_for_problem(pddl_domain, problem, verbose=verbose)


def evaluate_task_plans_and_costs_for_problem(
    pddl_domain, problem, planner=TASK_PLANNER_FD, verbose=False
):
    pass


planner = FD(alias_flag='--alias "lama-first"')


def plan(domain_fname, problem_fname):
    global planner
    try:
        plan = planner.plan_from_pddl(domain_fname, problem_fname, timeout=2)
    except PlanningFailure as pf:
        return False, pf
    except PlanningTimeout as pt:
        print("timed out")
        return False, pt
    return True, plan


def attempt_domain(domain_str, problem_str):
    with NamedTemporaryFile(mode="w") as domain_file, NamedTemporaryFile(
        mode="w"
    ) as problem_file:
        domain_file.write(domain_str)
        problem_file.write(problem_str)
        domain_file.flush()
        problem_file.flush()
        success, out = plan(domain_file.name, problem_file.name)
        return (success, out)
