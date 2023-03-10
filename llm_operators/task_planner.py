"""
task_planner.py
Utilities for generating task level plans.
"""

from collections import defaultdict
import os
import json
import random
from tempfile import NamedTemporaryFile
from typing import Optional, Sequence
import copy

from pddlgym_planners.fd import FD
from pddlgym_planners.planner import PlanningFailure, PlanningTimeout

from llm_operators.pddl import PDDLPlan

TASK_PLANNER_FD = "task_planner_fd"
TASK_PLANNER_PDSKETCH_ONTHEFLY = "task_planner_pdsketch_onthefly"


def evaluate_task_plans_and_costs_for_problems(
    pddl_domain,
    problems,
    command_args,
    verbose=False,
    output_directory=None,
    use_mock=False,
    debug_skip=False,
    proposed_operators: Optional[Sequence[str]] = None,
    task_plan_with_constants=False,
    max_task_samples=4,
):
    """
    Runs task planner to evaluate task plans for a set of planning problems, given a PDDL domain.

    For now, this just runs using the first operator definition.
    :ret: problems updated with PDDL plans.
    """
    if debug_skip:
        print(f"debug_skip_task_plans_and_costs_for_problems on {len(problems)}.")
        return
    print(f"evaluate_task_plans_and_costs_for_problems on {len(problems)}.")

    output_json = []
    experiment_tag = (
        ""
        if len(command_args.experiment_name) < 1
        else f"{command_args.experiment_name}_"
    )

    output_filepath = f"{experiment_tag}task_plans.json"

    if use_mock:
        mock_evaluate_task_plans_and_costs_for_problems(
            output_filepath, output_directory, problems
        )
        return

    if verbose:
        print(f"Use ground truth goals? {command_args.debug_ground_truth_goals}")

    # Set of proposed operators to work with when sampling task plans.
    if proposed_operators is None:
        proposed_operators = pddl_domain.proposed_operators.keys()

    total_solved_problems = 0
    for max_problems, problem_id in enumerate(problems):
        ###### DEBUGGING CLEAN ########
        if max_problems != 95:
            continue

        if verbose:
            print(
                f"\nNow on problem {max_problems} / {len(problems)}. Total solved problems so far: {total_solved_problems}"
            )
        any_success, problem_json = sample_task_plans_for_problem(
            pddl_domain=pddl_domain,
            problem=problems[problem_id],
            planner_type=command_args.planner,
            verbose=verbose,
            debug_ground_truth_goals=command_args.debug_ground_truth_goals,
            proposed_operators=proposed_operators,
            max_task_samples=max_task_samples,
        )
        if any_success:
            total_solved_problems += 1
        output_json.append(problem_json)
    if output_directory:
        with open(os.path.join(output_directory, output_filepath), "w") as f:
            json.dump(output_json, f)


def generate_random_proposed_operator_samples(
    proposed_operators, num_samples=4, sample_percent=0.5
):
    # Sample some percentage of the operator
    num_to_sample = int(sample_percent * len(proposed_operators))
    return [
        random.sample(proposed_operators, num_to_sample) for _ in range(num_samples)
    ]


def sample_task_plans_for_problem(
    pddl_domain,
    problem,
    planner_type=TASK_PLANNER_FD,
    verbose=False,
    debug_ground_truth_goals=False,
    proposed_operators: Optional[Sequence[str]] = None,
    max_task_samples=4,
):
    overall_problem_json = {"file_name": problem.problem_id, "plans": []}
    any_success = False
    all_evaluated_plans = defaultdict(set)
    for sampled_proposed_operators in generate_random_proposed_operator_samples(
        proposed_operators, max_task_samples - 2
    ) + [[], proposed_operators]:
        # If we've already succeeded, do not run with all proposed operators.
        if len(sampled_proposed_operators) == len(proposed_operators) and any_success:
            continue
        else:
            # First attempt to run the planner with all of the operators.
            success, evaluated_plans, _ = run_planner(
                pddl_domain=pddl_domain,
                problem=problem,
                planner_type=planner_type,
                verbose=verbose,
                debug_ground_truth_goals=debug_ground_truth_goals,
                proposed_operators=sampled_proposed_operators,
            )
            any_success = any_success or success
            for g in evaluated_plans:
                all_evaluated_plans[g].add(evaluated_plans[g])

    for g in all_evaluated_plans:
        for pddl_plan in all_evaluated_plans[g]:
            overall_problem_json["plans"].append({"goal": g, "plan": pddl_plan.plan})
        print(f"Found a total of {len(all_evaluated_plans[g])} unique plans for goal.")
    return any_success, overall_problem_json


def mock_evaluate_task_plans_and_costs_for_problems(
    output_filepath, output_directory, problems
):
    with open(os.path.join(output_directory, output_filepath), "r") as f:
        output_json = json.load(f)
        print(
            f"Now in: mock_evaluate_task_plans_and_costs_for_problems: from {os.path.join(output_directory, output_filepath)}"
        )
    for plan in output_json:
        if plan["file_name"] in problems:
            problem = problems[plan["file_name"]]
            for plan_json in plan["plans"]:
                # This updates the evaluated PDDL task plans that succeeded.
                problem.evaluated_pddl_plans[plan_json["goal"]] = PDDLPlan(
                    plan=plan_json["plan"]
                )
    print(
        f"After initialization, there are {len([p for p in problems if len(problems[p].evaluated_pddl_plans) > 0])} problems with plans."
    )


def run_planner(
    pddl_domain,
    problem,
    planner_type=TASK_PLANNER_FD,
    verbose=False,
    debug_ground_truth_goals=False,
    proposed_operators: Optional[Sequence[str]] = None,
):
    """
    pddl_domain: Domain object.
    problem: Problem object.
    planner_type: string indicating which planenr to use.

    :ret: Attempts to run planner on each goal in problem.proposed_pddl_goals.
    any_success: whether any of the goals succeeded.
    evaluated_plans : {goal : Plan}
    """
    output_json = {"file_name": problem.problem_id, "plans": []}

    # Get domain strings. Pick the first one that parses
    current_domain_string = pddl_domain.to_string(
        ground_truth_operators=False,
        current_operators=True,
        proposed_operators=proposed_operators,
        show_constants=(not problem.constants_in_problem_file),
    )
    if verbose:
        print(
            f"Running planner with existing operators + {len(proposed_operators)} proposed operators: "
        )
        print(proposed_operators)

    if debug_ground_truth_goals:
        goals = [problem.ground_truth_pddl_problem.ground_truth_goal]
    else:
        goals = problem.proposed_pddl_goals

    any_success = False
    evaluated_plans = dict()
    for goal in goals:
        current_problem_string = problem.ground_truth_pddl_problem.get_pddl_string_with_proposed_goal(
            proposed_goal=goal
        )
        if verbose:
            print("Ground truth goal: ")
            print(problem.ground_truth_pddl_problem.ground_truth_goal)
            print("Proposed goal:")
            print(goal)
        if planner_type == TASK_PLANNER_FD:
            success, plan_string = fd_plan_from_strings(
                domain_str=current_domain_string,
                problem_str=current_problem_string,
                verbose=verbose,
            )
        elif planner_type == TASK_PLANNER_PDSKETCH_ONTHEFLY:
            success, plan_string = pdsketch_onthefly_plan_from_strings(
                domain_str=current_domain_string, problem_str=current_problem_string
            )
        else:
            raise ValueError(f"Unknown planner type: {planner_type}")
        # Convert the planner into a plan object.
        if success:
            pddl_plan = PDDLPlan(plan_string=plan_string, pddl_domain=pddl_domain)
            evaluated_plans[goal] = pddl_plan
            if verbose:
                print(plan_string)
            output_json["plans"].append({"goal": goal, "plan": pddl_plan.plan})
            any_success = True
    if verbose:
        print(
            f"Found {len(evaluated_plans)}/{len(goals)} evaluated plans for proposed goals"
        )
    return any_success, evaluated_plans, output_json


def fd_plan_from_strings(domain_str, problem_str, timeout=10, verbose=False):
    with NamedTemporaryFile(mode="w") as domain_file, NamedTemporaryFile(
        mode="w"
    ) as problem_file:
        domain_file.write(domain_str)
        problem_file.write(problem_str)
        domain_file.flush()
        problem_file.flush()
        success, out = fd_plan_from_file(
            domain_file.name, problem_file.name, timeout=timeout
        )
        return (success, out)


def fd_plan_from_file(domain_fname, problem_fname, timeout=5):
    # TBD: don't use PDDL gym planner, use original FD.
    fd_planner = FD(alias_flag='--alias "lama-first"')
    try:
        plan = fd_planner.plan_from_pddl(domain_fname, problem_fname, timeout=timeout)
        plan_string = "\n".join(["(" + a + ")" for a in plan])
    except PlanningFailure as pf:
        return False, pf
    except PlanningTimeout as pt:
        print("Time out")
        return False, pt
    return True, plan_string


def pdsketch_onthefly_plan_from_strings(domain_str, problem_str, timeout=10):
    import concepts.pdsketch as pds

    domain = pds.load_domain_string(domain_str)
    problem = pds.load_problem_string(problem_str, domain, return_tensor_state=False)

    from concepts.pdsketch.strips.strips_grounding_onthefly import (
        OnTheFlyGStripsProblem,
    )

    gproblem = OnTheFlyGStripsProblem.from_domain_and_problem(domain, problem)

    from concepts.pdsketch.strips.strips_grounding_onthefly import ogstrips_search

    plan = ogstrips_search(gproblem, timeout=timeout)

    if plan is None:
        return False, None
    return (
        True,
        "\n".join([op.to_applier_pddl_str(arguments) for op, arguments in plan]),
    )

