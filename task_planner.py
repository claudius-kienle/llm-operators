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
): # move accurate plans to problem.evaluated
    # TODO: CW - see if this is working, fix it otherwise.
    for proposed_goal in problem.proposed_pddl_goals:
        # THIS SHOULD OUTPUT A WORKING PDDL PROBLEM STRING USING PROPOSED GOALS.
        # ALSO PLEASE CACHE THIS TO A FILE.
        pddl_problem_string = problem.ground_truth_pddl_problem.get_pddl_string_with_proposed_goal(
            proposed_goal)


    # fd_attempt_domain(pddl_domain.to_string(), pddl_problem_string)


def plan_with_alfred_metric_ff_planner(pddl_domain_file, pddl_problem_file):
    """"""
    from alfred.gen.ff_planner import get_plan_from_file

    args = (pddl_domain_file, pddl_problem_file, 3)  # 3: solver type.
    get_plan_from_file(args)


def fd_plan(domain_fname, problem_fname, planner=None):
    # TBD: don't use PDDL gym planner, use original FD.
    fd_planner = FD(alias_flag='--alias "lama-first"')
    try:
        plan = planner.plan_from_pddl(domain_fname, problem_fname, timeout=2)
    except PlanningFailure as pf:
        return False, pf
    except PlanningTimeout as pt:
        print("timed out")
        return False, pt
    return True, plan


def fd_attempt_domain(domain_str, problem_str):
    with NamedTemporaryFile(mode="w") as domain_file, NamedTemporaryFile(
        mode="w"
    ) as problem_file:
        domain_file.write(domain_str)
        problem_file.write(problem_str)
        domain_file.flush()
        problem_file.flush()
        success, out = fd_plan(domain_file.name, problem_file.name)

        return (success, out)
