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
    pddl_domain,
    problems,
    command_args,
    verbose=False,
    output_directory=None,
    use_mock=False,
    dataset_name="",
):
    """
    Runs a motion planner.
    """
    if "alfred" in dataset_name:
        evaluate_alfred_motion_plans_and_costs_for_problems(
            pddl_domain,
            problems,
            command_args,
            verbose=verbose,
            output_directory=output_directory,
            use_mock=use_mock,
        )
    else:
        print(f"Unsupported dataset name: {dataset_name}")
        assert False


def mock_alfred_motion_plans_and_costs_for_problems(
    output_filepath, output_directory, problems
):
    assert False


def evaluate_alfred_motion_plans_and_costs_for_problems(
    pddl_domain,
    problems,
    command_args,
    verbose=False,
    output_directory=None,
    use_mock=False,
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
        return
    for max_problems, problem_id in enumerate(problems):
        for pddl_goal in problems[problem_id].evaluated_pddl_plans:
            plan = problems[problem_id].evaluated_pddl_plans[pddl_goal]
            if plan is not None and plan != {}:
                if verbose:
                    print(f"Motion planning for: {problem_id}")
                    print(f"Proposed goal is: ")
                    print(pddl_goal)
                    print(f"Ground truth oracle goal is: ")
                    print(
                        problems[problem_id].ground_truth_pddl_problem.ground_truth_goal
                    )
                    # Convert plan to sequential plan predicates.
                    postcondition_predicates_json = plan.to_postcondition_predicates_json(
                        pddl_domain, remove_alfred_object_ids=True
                    )
                    import pdb

                    pdb.set_trace()
                    # TODO: [PS] overwrite this.
                    attempt_sequential_plan_alfred(
                        problem_id, plan, pddl_domain, verbose
                    )
                    # TODO: check if the oracle goal was actually satisfied. This is: problems[problem_id].ground_truth_pddl_problem.ground_truth_goal; but Jiahai also implements a separate oracle class.


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
