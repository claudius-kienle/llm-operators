"""
motion_planner.py
Utilities for generating motion plans.
"""
from pddl import PDDLPlan
import os, sys

os.environ["ALFRED_ROOT"] = os.path.join(os.getcwd(), "alfred")
sys.path.append(os.path.join(os.environ["ALFRED_ROOT"]))
sys.path.append(os.path.join(os.environ["ALFRED_ROOT"], "gen"))

from alfred.alfredplanner import init_alfred, search, Literal, Fluent


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


def evaluate_alfred_motion_plans_and_costs_for_goal_plan(
    problem_id, problems, pddl_goal, pddl_plan, pddl_domain, verbose, debug_skip=False
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
        # Not yet implemented.
        assert False


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


def attempt_sequential_plan_alfred(
    problem_id, pddl_plan, pddl_domain, verbose=False, num_rollouts_per_action=500
):
    """"pddl_plan: a PDDLPlan object with operators on it. Attempts to execute a plan step by step, satisfying a series of postconditions."""
    # Initialize the ALFRED environment for the problem.
    motion_plan = {"successful_actions": [], "oracle_success": []}

    # TODO [PS/CW]: initialize to the correct task: use problem_id, which is a path name like 'train/pick_and_place_simple-CellPhone-None-Drawer-302/trial_T20190907_235412_132976'
    sim_env = init_alfred(task_idx=1)

    for action in pddl_plan.plan:
        print("Attempting to ex")
        ground_postcondition_predicates = PDDLPlan.get_postcondition_predicates(
            action, pddl_domain
        )

        # TODO [PS / CW]: check that these predicates are implemented in Alfred. A predicate is a PDDLPredicate defined in pddl.py.
        # argument_values are currently a list of object_ids; these should be changed to object types.
        ground_postcondition_fluents = [
            Literal(
                fluent=Fluent(
                    predicate=predicate.name, objects=list(predicate.argument_values),
                ),
                neg=predicate.neg,
            )
            for predicate in ground_postcondition_predicates
        ]

        success, traj = search(
            sim_env, ground_postcondition_fluents, num_roll_outs=1000,
        )
        if success:
            motion_plan["successful_actions"].append(
                {"task_action": action, "motion_trajectory": traj}
            )
        else:
            motion_plan["oracle_success"] = False
            return motion_plan
