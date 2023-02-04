"""
motion_planner.py
Utilities for generating motion plans.
"""

import os
import alfred.alfredplanner as alfredplanner

from llm_operators.pddl import PDDLPlan
from llm_operators.experiment_utils import RANDOM_SEED


def evaluate_motion_plans_and_costs_for_problems(
    curr_iteration,
    pddl_domain,
    problems,
    command_args,
    verbose=False,
    output_directory=None,
    use_mock=False,
    debug_skip=False,
    dataset_name="",
):
    """
    Runs a motion planner.
    """
    if "alfred" in dataset_name:
        evaluate_alfred_motion_plans_and_costs_for_problems(
            curr_iteration,
            pddl_domain,
            problems,
            command_args,
            verbose=verbose,
            output_directory=output_directory,
            use_mock=use_mock,
            debug_skip=debug_skip,
        )
    else:
        print(f"Unsupported dataset name: {dataset_name}")
        assert False


def mock_alfred_motion_plans_and_costs_for_problems(
    output_filepath, output_directory, problems
):
    assert False


def evaluate_alfred_motion_plans_and_costs_for_problems(
    curr_iteration,
    pddl_domain,
    problems,
    command_args,
    verbose=False,
    output_directory=None,
    use_mock=False,
    debug_skip=False,
):
    print(f"evaluate_motion_plans_and_costs_for_problems on {len(problems)} problems.")
    output_json = []
    experiment_tag = (
        ""
        if len(command_args.experiment_name) < 1
        else f"{command_args.experiment_name}_"
    )
    output_filepath = f"{experiment_tag}motion_plans.json"

    if use_mock:
        mock_alfred_motion_plans_and_costs_for_problems(
            output_filepath, output_directory, problems
        )
        # Not implemented
        assert False

    for max_problems, problem_id in enumerate(problems):
        for pddl_goal in problems[problem_id].evaluated_pddl_plans:
            pddl_plan = problems[problem_id].evaluated_pddl_plans[pddl_goal]
            if pddl_plan is not None and pddl_plan != {} and pddl_plan.plan is not None:
                # run_motion_planner
                # not implemented envname to task_id
                # recording videos. quicktime player.
                motion_plan_result = evaluate_alfred_motion_plans_and_costs_for_goal_plan(
                    problem_id,
                    problems,
                    pddl_goal,
                    pddl_plan,
                    pddl_domain,
                    verbose,
                    debug_skip=debug_skip,
                )
                problems[problem_id].evaluated_motion_planner_results[
                    pddl_goal
                ] = motion_plan_result
                if motion_plan_result.task_success:
                    problems[
                        problem_id
                    ].best_evaluated_plan_at_iteration = curr_iteration
                if verbose:
                    print(
                        f"Motion plan result: task_success: {motion_plan_result.task_success}"
                    )
                    print(
                        f"Successfully executed: {motion_plan_result.last_failed_operator} / {len(motion_plan_result.pddl_plan.plan)} operators in task plan.\n\n\n"
                    )


def evaluate_alfred_motion_plans_and_costs_for_goal_plan(
    problem_id, problems, pddl_goal, pddl_plan, pddl_domain, verbose, debug_skip=False,
):
    if verbose:
        print(f"Motion planning for: {problem_id}")
        print(f"Proposed goal is: ")
        print(pddl_goal)
        print(f"Ground truth oracle goal is: ")
        print(problems[problem_id].ground_truth_pddl_problem.ground_truth_goal)
    # Convert plan to sequential plan predicates.
    postcondition_predicates_json = pddl_plan.to_postcondition_predicates_json(
        pddl_domain, remove_alfred_object_ids=True
    )
    if debug_skip:
        return MotionPlanResult(
            pddl_plan=pddl_plan,
            postcondition_predicates_json=postcondition_predicates_json,
            task_success=True,
            last_failed_operator=None,
            last_failed_predicate=None,
            debug_skip=debug_skip,
        )
    else:
        # Run the motion planner.
        dataset_split = os.path.split(problem_id)[0]
        task_name = os.path.join(*os.path.split(problem_id)[1:])
        if verbose:
            print("Attempting to execute the following motion plan:")
            print(postcondition_predicates_json)

            print("Ground truth PDDL plan is: ")
            print(problems[problem_id].ground_truth_pddl_plan.plan_string)
        alfred_motion_task = {
            "task": task_name,
            "repeat_idx": 0,  # How do we know which one it is?
        }
        raw_motion_plan_result = alfredplanner.run_motion_planner(
            task=alfred_motion_task,
            operator_sequence=postcondition_predicates_json,
            robot_init=RANDOM_SEED,
            dataset_split=dataset_split,
        )

        return MotionPlanResult(
            pddl_plan=pddl_plan,
            postcondition_predicates_json=postcondition_predicates_json,
            task_success=raw_motion_plan_result["task_success"],
            last_failed_operator=raw_motion_plan_result["last_failed_operator"],
            last_failed_predicate=raw_motion_plan_result["last_failed_predicate"],
            debug_skip=debug_skip,
        )


class MotionPlanResult:
    # A motion planning result.
    def __init__(
        self,
        pddl_plan,
        postcondition_predicates_json,
        task_success,
        last_failed_operator,
        last_failed_predicate,
        debug_skip=False,
    ):
        """
        task_success: bool
        last_failed_operator: returns index of last failed operator.
        last_failed_predicate: return last failed predicate in that operator.
        """
        self.pddl_plan = pddl_plan  # PDDLPlan
        self.postcondition_predicates_json = postcondition_predicates_json
        self.task_success = task_success
        self.last_failed_operator = last_failed_operator if not debug_skip else None
        self.last_failed_predicate = (
            last_failed_predicate
            if not debug_skip
            else self.postcondition_predicates_json[-1][
                PDDLPlan.PDDL_GROUND_PREDICATES
            ][-1]
        )

