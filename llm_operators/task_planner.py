"""
task_planner.py
Utilities for generating task level plans.
"""

import os
import os.path as osp
import json
import random
import csv
from collections import defaultdict
from tempfile import NamedTemporaryFile
from typing import Optional, Sequence
import scipy as scipy

from pddlgym_planners.fd import FD
from pddlgym_planners.planner import PlanningFailure, PlanningTimeout

from llm_operators.pddl import PDDLPlan

TASK_PLANNER_FD = "task_planner_fd"
TASK_PLANNER_PDSKETCH_ONTHEFLY = "task_planner_pdsketch_onthefly"
TASK_PLANNER_PDSKETCH_ONTHEFLY_HMAX = "task_planner_pdsketch_onthefly_hmax"
TASK_PLANNER_PDSKETCH_ONTHEFLY_HFF = "task_planner_pdsketch_onthefly_hff"


def attempt_task_plan_for_problem(
    pddl_domain,
    problem_idx,
    problem_id,
    problems,
    command_args,
    verbose=False,
    output_directory=None,
    use_mock=False,
    debug_skip=False,
    task_plan_with_constants=False,
    plan_attempt_idx=0,
    max_task_samples=4,
    goal_idx=None,
    debug_proposed_operators: Optional[Sequence[str]] = None,  # Debugging only.
    random_generator=None,
    minimum_n_operators=1,
    resume_from_iteration=0,
    resume_from_problem_idx=0,
    curr_iteration=0,
):
    """
    Evaluates planner to evaluate task plans for a single planning problems, given a PDDL domain.
    :ret: TRUE if we've added a new PDDL plan for a goal. Updates problem for task plan.
    """
    if plan_attempt_idx == 0:
        print(
            f"task_planner.attempt_task_plan_for_problem: attempt {plan_attempt_idx} : {problem_idx} / {len(problems)}, {problem_id}"
        )
    else:
        print(f"\ttask_planner.attempt_task_plan_for_problem: attempt {plan_attempt_idx}, {problem_id}")
    if debug_skip:
        print("\t...debug_skip.")

    experiment_tag = "" if len(command_args.experiment_name) < 1 else f"{command_args.experiment_name}_"

    # NB(Jiayuan Mao @ 2023/04/07): this file is solved via pddl.checkpoint_and_reset_plans function.
    output_filepath = f"{experiment_tag}task_plans.json"

    if use_mock and curr_iteration <= resume_from_iteration and problem_idx <= resume_from_problem_idx:
        unsolved_problems = mock_evaluate_task_plans_and_costs_for_problems(
            output_filepath, output_directory, problems
        )
        if problem_id in unsolved_problems or len(problems[problem_id].evaluated_pddl_plans) > 0:
            print("Mock found for task plan, continuing...")
            any_success = True
            new_evaluated_plans = problems[problem_id].evaluated_pddl_plans
            return any_success, new_evaluated_plans
        else:
            print("Mock not found for task plan, continuing...")

    if command_args.debug_export_failed_pddl:
        # NB(Jiayuan Mao @ 2023/04/07): do a bit of hack here, because we don't have access to "current_iteration" here.
        debug_export_dir = os.path.join(
            command_args.debug_export_failed_pddl,
            osp.basename(output_directory),
            f"problem_{problem_idx}_attempt_{plan_attempt_idx}",
        )
    else:
        debug_export_dir = None

    any_success, new_evaluated_plans, problem_json = sample_task_plans_for_problem(
        pddl_domain=pddl_domain,
        problem=problems[problem_id],
        planner_type=command_args.planner,
        command_args=command_args,
        verbose=verbose,
        output_directory=output_directory,
        debug_ground_truth_goals=command_args.debug_ground_truth_goals,
        debug_proposed_operators=debug_proposed_operators,
        debug_export_dir=debug_export_dir,
        plan_attempt_idx=plan_attempt_idx,
        goal_idx=goal_idx,
        random_generator=random_generator,
        minimum_n_operators=minimum_n_operators,
    )
    if any_success:
        # Check that this isn't a duplicate of a plan we've already found for that same problem.
        any_success = problems[problem_id].update_evaluated_pddl_plans(new_evaluated_plans)
    return any_success, new_evaluated_plans


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
    Batch evaluates planner to evaluate task plans for a set of planning problems, given a PDDL domain.

    For now, this just runs using the first operator definition.
    :ret: problems updated with PDDL plans.
    """
    if debug_skip:
        print(f"debug_skip_task_plans_and_costs_for_problems on {len(problems)}.")
        return
    print(f"evaluate_task_plans_and_costs_for_problems on {len(problems)}.")

    output_json = []
    experiment_tag = "" if len(command_args.experiment_name) < 1 else f"{command_args.experiment_name}_"

    output_filepath = f"{experiment_tag}task_plans.json"

    if use_mock:
        mock_evaluate_task_plans_and_costs_for_problems(output_filepath, output_directory, problems)
        return

    if verbose:
        print(f"Use ground truth goals? {command_args.debug_ground_truth_goals}")

    total_solved_problems = 0
    for max_problems, problem_id in enumerate(problems):
        if verbose:
            print(
                f"\nNow on problem {max_problems} / {len(problems)}. Total solved problems so far: {total_solved_problems}"
            )
        any_success, new_evaluated_plans, problem_json = sample_task_plans_for_problem(
            pddl_domain=pddl_domain,
            problem=problems[problem_id],
            planner_type=command_args.planner,
            command_args=command_args,
            verbose=verbose,
            output_directory=output_directory,
            debug_ground_truth_goals=command_args.debug_ground_truth_goals,
            proposed_operators=proposed_operators,
            max_task_samples=max_task_samples,
        )
        problems[problem_id].update_evaluated_pddl_plans(new_evaluated_plans)
        if any_success:
            total_solved_problems += 1
        output_json.append(problem_json)
    if output_directory:
        with open(os.path.join(output_directory, output_filepath), "w") as f:
            json.dump(output_json, f)


def get_top_k_operators_to_cover_operator_downsampling_percentage(
    categorical_operator_scores, operator_downsampling_percentage
):
    # If we greedily chose the operators,
    sorted_scores = sorted(categorical_operator_scores, reverse=True)
    total_percentage = 0
    for idx, score in enumerate(sorted_scores):
        total_percentage += score
        if total_percentage >= operator_downsampling_percentage:
            return idx + 1


def generate_random_proposed_operator_sample(pddl_domain, minimum_n_operators, random_generator, max_attempts=5):
    """
    Samples a set of at least minimum_n_operators operators.
    We choose to include each operator independently based on p(n_operator_successes / n_operator_attempts) in previous trials.
    We make at most max passes through the operator set to do so.
    """
    sampled_operators = set()
    proposed_operators = pddl_domain.proposed_operators
    for n_sampling_attempts in range(max_attempts):
        for operator_name in pddl_domain.proposed_operators:
            for operator_body in pddl_domain.proposed_operators[operator_name]:
                (n_operator_successes, n_operator_attempts) = pddl_domain.operators_to_scores[
                    (operator_name, operator_body)
                ]
                # Flip(p) where p(n_operator_successes / n_operator_attempts)
                if random_generator.binomial(1, float(n_operator_successes / n_operator_attempts), 1)[0] > 0:
                    sampled_operators.add(operator_name)
        if len(sampled_operators) >= minimum_n_operators:
            return sampled_operators
    return sampled_operators


def sample_task_plans_for_problem(
    pddl_domain,
    problem,
    planner_type=TASK_PLANNER_FD,
    command_args=None,
    verbose=False,
    output_directory=None,
    debug_ground_truth_goals=False,
    debug_proposed_operators: Optional[Sequence[str]] = None,
    debug_export_dir=None,
    plan_attempt_idx=0,
    goal_idx=None,
    random_generator=None,
    minimum_n_operators=None,
):
    """
    Uses a task_planner to propose samples, so we attempt planning using random subsets of
    proposed_operator set to get a diverse set of plans.

    :ret:
    any_success - whether any of the task plans succeeded.
    all_evaluated_plans: dict(goal : set(plans for this goal))
    overall_problem_json: serializable JSON format.
    """
    overall_problem_json = {"file_name": problem.problem_id, "plans": []}
    any_success = False

    # From the valid operator set, further downsample a set of operators to try, to prevent timeouts and promote operator diversity.
    if debug_proposed_operators:
        sampled_proposed_operators = debug_proposed_operators
    else:
        sampled_proposed_operators = generate_random_proposed_operator_sample(
            pddl_domain=pddl_domain,
            minimum_n_operators=minimum_n_operators,
            random_generator=random_generator,
        )
    success, evaluated_plans, _ = run_planner(
        pddl_domain=pddl_domain,
        problem=problem,
        planner_type=planner_type,
        verbose=verbose,
        debug_ground_truth_goals=debug_ground_truth_goals,
        proposed_operators=sampled_proposed_operators,
        debug_export_dir=debug_export_dir,
        goal_idx=goal_idx,
    )

    any_success = any_success or success
    for g in evaluated_plans:
        overall_problem_json["plans"].append({"goal": g, "plan": evaluated_plans[g].plan})
    print(f"Sucessfully found {len(evaluated_plans)} plans for goals.")

    if output_directory:
        experiment_tag = "" if len(command_args.experiment_name) < 1 else f"{command_args.experiment_name}_"
        output_filepath = f"{experiment_tag}task_planner_results.csv"
        output_filepath = osp.join(output_directory, output_filepath)

        if not osp.exists(output_filepath):
            with open(output_filepath, "w") as f:
                csv.writer(f).writerow(
                    ["problem_id", "attempt_id", "minimum_n_operators", "goal", "success", "plan", "sampled_operators"]
                )
        with open(output_filepath, "a") as f:
            writer = csv.writer(f)
            if debug_ground_truth_goals:
                goals = [problem.ground_truth_pddl_problem.ground_truth_goal]
            else:
                goals = problem.proposed_pddl_goals
            for goal in goals:
                writer.writerow(
                    [
                        problem.problem_id,
                        plan_attempt_idx,
                        minimum_n_operators,
                        goal,
                        goal in evaluated_plans,
                        evaluated_plans[goal].plan_string if goal in evaluated_plans else None,
                        str(list(sampled_proposed_operators)),
                    ]
                )

    return any_success, evaluated_plans, overall_problem_json


def mock_evaluate_task_plans_and_costs_for_problems(output_filepath, output_directory, problems):
    unsolved_problems = set()
    with open(os.path.join(output_directory, output_filepath), "r") as f:
        output_json = json.load(f)
        print(
            f"Now in: mock_evaluate_task_plans_and_costs_for_problems: from {os.path.join(output_directory, output_filepath)}"
        )
    for plan in output_json:
        if plan["file_name"] in problems:
            problem = problems[plan["file_name"]]
            if len(plan["plans"]) == 0:
                unsolved_problems.add(plan["file_name"])
            else:
                # Set each goal to the set of plans, not a list.
                for plan_json in plan["plans"]:
                    # This updates the evaluated PDDL task plans that succeeded.
                    plan = PDDLPlan(plan=plan_json["plan"])
                    if plan not in set(problem.evaluated_pddl_plans[plan_json["goal"]]):
                        problem.evaluated_pddl_plans[plan_json["goal"]].append(plan)
    print(
        f"After initialization, there are {len([p for p in problems if len(problems[p].evaluated_pddl_plans) > 0])} problems with plans."
    )
    return unsolved_problems


def run_planner(
    pddl_domain,
    problem,
    planner_type=TASK_PLANNER_FD,
    verbose=False,
    debug_ground_truth_goals=False,
    proposed_operators: Optional[Sequence[str]] = None,
    debug_export_dir=None,
    goal_idx=None,
):
    """
    pddl_domain: Domain object.
    problem: Problem object.
    planner_type: string indicating which planner to use.
    goal_idx: run planner on a specific goal.

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

    if debug_ground_truth_goals:
        sorted_goals = [problem.ground_truth_pddl_problem.ground_truth_goal]
    else:
        sorted_goals = sorted(problem.proposed_pddl_goals)
    if len(sorted_goals) < 1:
        print("\t...no goals, skipping.")

    any_success = False
    evaluated_plans = dict()

    # These must be sorted for this to make sense.
    for current_goal_idx, goal in enumerate(sorted_goals):
        if goal_idx is not None and current_goal_idx != goal_idx:
            continue
        else:
            print(f"Now attempting to plan for goal: {goal_idx} / {len(sorted_goals)}")
            if verbose:
                print(f"\tRunning planner with existing operators + {len(proposed_operators)} proposed operators: ")
                print(f"\t Initial Operators: {pddl_domain.operators.keys()}")
                print(f"\t Proposed Operators: {proposed_operators}")
            current_problem_string = problem.ground_truth_pddl_problem.get_pddl_string_with_proposed_goal(
                proposed_goal=goal
            )
            if verbose:
                print("\t Language:")
                print("\t" + problem.language)
                print("\t Ground truth goal: ")
                print("\t" + problem.ground_truth_pddl_problem.ground_truth_goal)
                print("\t Proposed goal:")
                print("\t" + goal)
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
            elif planner_type == TASK_PLANNER_PDSKETCH_ONTHEFLY_HMAX:
                success, plan_string = pdsketch_onthefly_plan_from_strings(
                    domain_str=current_domain_string,
                    problem_str=current_problem_string,
                    heuristic="hmax",
                )
            elif planner_type == TASK_PLANNER_PDSKETCH_ONTHEFLY_HFF:
                success, plan_string = pdsketch_onthefly_plan_from_strings(
                    domain_str=current_domain_string,
                    problem_str=current_problem_string,
                    heuristic="hff",
                )
            else:
                raise ValueError(f"Unknown planner type: {planner_type}")
            # Convert the planner into a plan object.
            if verbose:
                print(f"\tPlan success: {success}")
                print(f"\t Plan string: {plan_string}")
            if success:
                try:
                    pddl_plan = PDDLPlan(plan_string=plan_string, pddl_domain=pddl_domain)
                    evaluated_plans[goal] = pddl_plan
                    output_json["plans"].append({"goal": goal, "plan": pddl_plan.plan})
                    any_success = True
                except:
                    print(f"\t\tFailed to parse plan string: {plan_string}")
            else:
                if debug_export_dir is not None:
                    os.makedirs(debug_export_dir, exist_ok=True)
                    with open(osp.join(debug_export_dir, f"goal_{current_goal_idx}_domain.pddl"), "w") as f:
                        f.write(current_domain_string)
                    with open(osp.join(debug_export_dir, f"goal_{current_goal_idx}_problem.pddl"), "w") as f:
                        f.write(current_problem_string)
                    print(f"Exported domain and problem to {debug_export_dir}")

    return any_success, evaluated_plans, output_json


def fd_plan_from_strings(domain_str, problem_str, timeout=10, verbose=False):
    with NamedTemporaryFile(mode="w") as domain_file, NamedTemporaryFile(mode="w") as problem_file:
        domain_file.write(domain_str)
        problem_file.write(problem_str)
        domain_file.flush()
        problem_file.flush()
        success, out = fd_plan_from_file(domain_file.name, problem_file.name, timeout=timeout)
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


def pdsketch_onthefly_plan_from_strings(domain_str, problem_str, timeout=10, heuristic=None):
    import concepts.pdsketch as pds

    domain = pds.load_domain_string(domain_str)
    problem = pds.load_problem_string(problem_str, domain, return_tensor_state=False)

    from concepts.pdsketch.strips.strips_grounding_onthefly import (
        OnTheFlyGStripsProblem,
    )

    gproblem = OnTheFlyGStripsProblem.from_domain_and_problem(domain, problem)
    # import ipdb; ipdb.set_trace()

    if heuristic is None:
        from concepts.pdsketch.strips.strips_grounding_onthefly import ogstrips_search

        plan = ogstrips_search(gproblem, timeout=timeout, initial_actions=[])
    elif heuristic == "hmax":
        from concepts.pdsketch.strips.strips_grounding_onthefly import ogstrips_search_with_heuristics

        # plan = ['move-right(t1, t2)', 'move-right(t2, t3)', 'move-right(t3, t4)', 'move-right(t4, t5)', 'move-right(t5, t6)', 'move-right(t6, t7)', 'move-right(t7, t8)', 'move-right(t8, t9)', 'pick-up(t9, o5, i2)', 'move-right(t9, t10)', 'harvest-sugar-cane(i3, t10, t0, o5, o10, i2, o17)']
        # canonized_plan = _pdsketch_get_canonized_plan(gproblem, plan)
        # plan = ogstrips_search_with_heuristics(gproblem, initial_actions=canonized_plan, timeout=timeout, hfunc_name='hmax', verbose=True, hfunc_verbose=True)
        plan = ogstrips_search_with_heuristics(gproblem, timeout=timeout, hfunc_name="hmax", g_weight=0.5)
    elif heuristic == "hff":
        from concepts.pdsketch.strips.strips_grounding_onthefly import ogstrips_search_with_heuristics

        plan = ogstrips_search_with_heuristics(gproblem, timeout=timeout, hfunc_name="hff", g_weight=0)
    else:
        raise ValueError(f"Unknown heuristic: {heuristic}")

    if plan is None:
        return False, None
    return (
        True,
        "\n".join([op.to_applier_pddl_str(arguments) for op, arguments in plan]),
    )


def pdsketch_onthefly_verify_plan_from_strings(domain_str, problem_str, plan):
    import concepts.pdsketch as pds

    domain = pds.load_domain_string(domain_str)
    problem = pds.load_problem_string(problem_str, domain, return_tensor_state=False)

    from concepts.pdsketch.strips.strips_grounding_onthefly import (
        OnTheFlyGStripsProblem,
    )

    gproblem = OnTheFlyGStripsProblem.from_domain_and_problem(domain, problem)

    from concepts.pdsketch.strips.strips_grounding_onthefly import ogstrips_verify

    ogstrips_verify(gproblem, [action.lower() for action in plan], from_fast_downward=True)


def _pdsketch_get_canonized_plan(gproblem, plan_strings):
    canonized_plan = list()
    for action in plan_strings:
        action_name = action.split("(")[0]
        action_args = action.split("(")[1].split(")")[0].split(", ")
        operator = gproblem.operators[action_name]
        canonized_plan.append((operator, {arg.name: value for arg, value in zip(operator.arguments, action_args)}))

    return canonized_plan
