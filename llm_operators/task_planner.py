"""
task_planner.py
Utilities for generating task level plans.
"""

import os
import json
from tempfile import NamedTemporaryFile

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
):
    """
    Runs task planner to evaluate task plans for a set of planning problems, given a PDDL domain.

    For now, this just runs using the first operator definition.
    :ret: problems updated with PDDL plans.
    """
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
    for max_problems, problem_id in enumerate(problems):
        if verbose:
            print(problems[problem_id].language)
        problem_json = run_planner(
            pddl_domain=pddl_domain,
            problem=problems[problem_id],
            planner_type=command_args.planner,
            verbose=verbose,
            debug_ground_truth_goals=command_args.debug_ground_truth_goals,
        )
        output_json.append(problem_json)
    if output_directory:
        with open(os.path.join(output_directory, output_filepath), "w") as f:
            json.dump(output_json, f)


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
):
    """
    pddl_domain: Domain object.
    problem: Problem object.
    planner_type: string indicating which planenr to use.

    :ret: Attempts to run planner on each goal in problem.proposed_pddl_goals.

    Updates problem.evaluated_pddl_plans to {
        goal : PDDLPlan
    } if a PDDLPlan is found, along with a score for this plan.
    """
    output_json = {"file_name": problem.problem_id, "plans": []}
    if debug_ground_truth_goals:
        goals = [problem.ground_truth_pddl_problem.ground_truth_goal]
    else:
        goals = problem.proposed_pddl_goals
    for goal in goals:
        current_problem_string = problem.ground_truth_pddl_problem.get_pddl_string_with_proposed_goal(
            proposed_goal=goal
        )
        if verbose:
            print("Ground truth goal: ")
            print(problem.ground_truth_pddl_problem.ground_truth_goal)
            print("Proposed goal:")
            print(goal)

        # Get domain strings. Pick the first one that parses.
        current_domain_string = pddl_domain.to_string(
            ground_truth_operators=False,
            current_operators=True,
            proposed_operators=pddl_domain.proposed_operators.keys(),
        )

        if planner_type == TASK_PLANNER_FD:
            success, plan_string = fd_plan_from_strings(
                domain_str=current_domain_string, problem_str=current_problem_string
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
            problem.evaluated_pddl_plans[goal] = pddl_plan
            if verbose:
                print(plan_string)
            output_json["plans"].append({"goal": goal, "plan": pddl_plan.plan})
    if verbose:
        print(
            f"Found {len(problem.evaluated_pddl_plans)}/{len(problem.proposed_pddl_goals)} evaluated plans for proposed goals"
        )
    return output_json


def fd_plan_from_strings(domain_str, problem_str, timeout=10):
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

    from concepts.pdsketch.strips.strips_grounding_onthefly import OnTheFlyGStripsProblem, ogstrips_generate_applicable_actions
    gproblem = OnTheFlyGStripsProblem.from_domain_and_problem(domain, problem)

    from concepts.pdsketch.strips.strips_grounding_onthefly import ogstrips_search
    plan = ogstrips_search(gproblem, timeout=timeout)

    if plan is None:
        return False, None
    return True, '\n'.join([op.to_applier_pddl_str(arguments) for op, arguments in plan])

