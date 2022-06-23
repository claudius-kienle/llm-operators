"""
main.py | LLM-operators.

Uses LLMs to infer planning operators.
"""
from collections import defaultdict
import os
import json
from pddl_parser import *
from planner import *


DEFAULT_DATASET = "jiahai"

DOMAINS_PREFIX = os.path.join(os.getcwd(), "domains")
GENERATED_PREFIX = os.path.join(os.getcwd(), "generated")
PROBLEMS_PREFIX = os.path.join(os.getcwd(), "problems")
PLANS_PREFIX = os.path.join(os.getcwd(), "plans")

MAX_ITERATIONS = 1
EVAL_EVERY = 1
DEFAULT_NUM_TRAIN_OPERATORS = 3


def load_domain(dataset):
    return DomainParser(os.path.join(DOMAINS_PREFIX, dataset + ".pddl"))


def load_problems(dataset):
    with open(os.path.join(PROBLEMS_PREFIX, dataset + ".json")) as f:
        raw_problems = json.load(f)
    problem_ids, problems = [], {}
    for problem in raw_problems:
        problem_id = problem["goal_id"]
        problem_ids.append(problem_ids)
        goal_language = problem["goal_language"]
        pddl_problem = problem["pddl_problem"]
        problems[problem_id] = Problem(
            pddl_problem=pddl_problem, goal_language=goal_language
        )
    return problem_ids, problems


def attempt_goals_pddl(domain, problems, assert_success=False):
    # Attempts to solve goals given a domain
    solved_plans = {}
    for idx, problem_id in enumerate(problems):
        if idx % 10 == 0:
            print(f"Planning now on {idx} / {len(problems)}")
        success, plan = attempt_domain(domain.domain, problems[problem_id].to_string())
        if assert_success:
            assert success
        solved_plans[problem_id] = plan
    return solved_plans


def maybe_update_gt(dataset, gt_plans, gt_domain, problems):
    no_gt_problems = {
        problem_id: problems[problem_id]
        for problem_id in problems.keys()
        if problem_id not in gt_plans
    }
    if len(no_gt_problems) > 0:
        solved_gt_plans = attempt_goals_pddl(
            gt_domain, no_gt_problems, assert_success=True
        )
        gt_plans.update(solved_gt_plans)
        with open(os.path.join(PLANS_PREFIX, dataset + ".json"), "w") as f:
            json.dump(gt_plans, f)
    return gt_plans


def get_train_domain_and_plans(
    gt_domain, gt_plans, num_train_operators=DEFAULT_NUM_TRAIN_OPERATORS
):
    gt_operators_to_problems = defaultdict(list)
    for operator in gt_domain.operators.keys():
        for problem_id, gt_plan in gt_plans.items():
            if operator in " ".join(gt_plan):
                gt_operators_to_problems[operator].append(problem_id)

    # Heuristic: remove all but the most common.
    operators_by_usage = sorted(
        gt_operators_to_problems.keys(), key=lambda o: len(gt_operators_to_problems[o])
    )
    train_operators = operators_by_usage[-DEFAULT_NUM_TRAIN_OPERATORS:]
    ablated_operators = [o for o in operators_by_usage if o not in train_operators]

    ablated_plans = set().union(
        *[gt_operators_to_problems[o] for o in ablated_operators]
    )
    train_plans = {
        plan_id: gt_plans[plan_id]
        for plan_id in gt_plans
        if plan_id not in ablated_plans
    }
    assert len(train_plans) > 0
    train_domain = get_train_domain(gt_domain, train_operators)
    return train_domain, train_plans


def load_plans(dataset, gt_domain, problems):
    train_plans, train_operators, gt_plans = {}, {}, {}
    with open(os.path.join(PLANS_PREFIX, dataset + ".json")) as f:
        gt_plans = json.load(f)

    # Plan for any goals that don't already exist.
    gt_plans = maybe_update_gt(dataset, gt_plans, gt_domain, problems)

    # Create a domain with an ablated set of operators.
    train_domain, train_plans = get_train_domain_and_plans(gt_domain, gt_plans)

    # Load plans or plan for them if need be.
    return train_plans, train_domain, gt_plans


def get_unsolved_goals_to_attempt_codex():
    pass


def get_proposed_plans_codex():
    pass


def get_proposed_operators_codex():
    pass


def update_train_domain():
    # Try updating the train domain with any operators and keep those that work.
    pass


def main():
    gt_domain = load_domain(dataset=DEFAULT_DATASET)
    (problem_ids, problems) = load_problems(dataset=DEFAULT_DATASET)

    train_plans, train_domain, gt_plans = load_plans(
        DEFAULT_DATASET, gt_domain, problems
    )

    for curr_iteration in range(MAX_ITERATIONS):
        if curr_iteration % EVAL_EVERY == 0:
            # Try to solve goals in PDDL
            solved_plans_pddl = attempt_goals_pddl(problems, train_domain)
            # TODO: try to solve goals low-level.
            solved_plans_low_level = solved_plans_pddl
        unsolved_goal_ids_to_attempt_codex = get_unsolved_goals_to_attempt_codex(
            problems, solved_plans_low_level
        )
        proposed_plan_sketches = get_proposed_plans_codex(
            unsolved_goal_ids_to_attempt_codex, problems, gt_domain, train_domain,
        )
        train_domain = update_train_domain(
            gt_domain, train_domain, proposed_plan_sketches
        )


if __name__ == "__main__":
    main()
