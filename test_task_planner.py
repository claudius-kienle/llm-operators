"""
test_task_planner.py
"""
import datasets
import pddl
import task_planner
from pddlgym_planners.ff import FF


def create_alfred_problem():
    alfred_dataset = datasets.load_alfred_planning_domain_problems(
        dataset_fraction=0.001
    )
    problem_id = list(alfred_dataset["train"].keys())[0]
    problem = alfred_dataset["train"][problem_id]
    problem.proposed_pddl_goals.append(
        problem.ground_truth_pddl_problem.ground_truth_goal
    )
    return problem


def test_run_planner_gt_operators_gt_goals():
    pddl_domain = datasets.load_alfred_pddl_domain()
    pddl_problem = create_alfred_problem()
    task_planner.run_planner(
        pddl_domain=pddl_domain, problem=pddl_problem, verbose=True
    )
    assert len(pddl_problem.proposed_pddl_goals) > 0
    for goal in pddl_problem.proposed_pddl_goals:
        assert len(pddl_problem.evaluated_pddl_plans[goal]) > 1
