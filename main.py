"""
main.py

Usage:  
    # Load a debug fraction of the ALFRED dataset.
    python main.py --experiment_name alfred_linearized_100 --dataset_name alfred_linearized_100 --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated/test_outputs 
    
    # Append these flags if you want to mock out the Codex proposals with previous checkpoints.
    --debug_mock_propose_plans --debug_mock_propose_operators --debug_mock_propose_goals 
    # Append this flag if you want to mock out the task planner with previous plans.
    --debug_mock_task_plans
"""
import argparse
import random
import codex
import datasets
import task_planner
import motion_planner
import pddl
import experiment_utils

parser = argparse.ArgumentParser()
parser.add_argument(
    "--experiment_name",
    type=str,
    default="",
    help="Experiment name tag. This will be appended to any checkpointed data.",
)
parser.add_argument(
    "--dataset_name", type=str, help="Name of the dataset of planning problems to load."
)
parser.add_argument(
    "--dataset_fraction",
    default=1.0,
    type=float,
    help="Fraction of the overall dataset to work with. Lower than 1.0 for debugging purposes",
)
parser.add_argument(
    "--training_plans_fraction",
    default=1.0,
    type=float,
    help="Fraction of the training problems to initialize with plans. Used to seed the Codex proposals.",
)
parser.add_argument(
    "--dataset_pddl_directory",
    type=str,
    help="Location of the top level PDDL directory.",
)
parser.add_argument(
    "--pddl_domain_name", type=str, help="Name of the PDDL domain to load.",
)

parser.add_argument(
    "--train_iterations", type=int, help="How many training iterations to run."
)
parser.add_argument(
    "--supervision_name",
    type=str,
    default="supervision",
    help="Tag for the supervision dataset to load.",
)

parser.add_argument(
    "--initial_plans_prefix",
    type=str,
    nargs="+",
    help="Which initial plan types to supervise on. Used to seed the Codex proposals",
)

parser.add_argument(
    "--initial_pddl_operators",
    type=str,
    nargs="+",
    help="Which initial PDDL operators to run with.  Used to seed the Codex proposals.",
)
parser.add_argument(
    "--initial_pddl_predicates",
    type=str,
    nargs="+",
    default=[],
    help="Which initial PDDL predicates to run with.  Used to seed the Codex proposals.",
)
parser.add_argument(
    "--planner", type=str, default="fd", help="Which planner to use.",
)
parser.add_argument(
    "--output_directory",
    type=str,
    help="Location of the directory for writing outputs.",
)
parser.add_argument("--verbose", action="store_true", help="Run on verbose.")
parser.add_argument(
    "--debug_no_propose_plans_operators_goals",
    action="store_true",
    help="debug: don't run propose_plans_operators_goals. Instead, use ground truths.",
)
parser.add_argument(
    "--debug_mock_propose_plans",
    action="store_true",
    help="debug: mock out plan proposal.",
)
parser.add_argument(
    "--debug_mock_propose_operators",
    action="store_true",
    help="debug: mock out operator_proposal.",
)
parser.add_argument(
    "--debug_mock_propose_goals",
    action="store_true",
    help="debug: mock out goal_proposal.",
)
parser.add_argument(
    "--debug_mock_task_plans",
    action="store_true",
    help="debug: mock out task plan symbolic search.",
)
parser.add_argument(
    "--debug_mock_motion_plans",
    action="store_true",
    help="debug: mock out motion plan grounded search.",
)
parser.add_argument(
    "--debug_skip_motion_plans",
    action="store_true",
    help="debug: skip motion plan grounded search and assume that all of the task plans succeeded.",
)

parser.add_argument(
    "--debug_ground_truth_goals",
    action="store_true",
    help="debug: use ground_truth_goals.",
)
parser.add_argument(
    "--top_n_operators",
    type=int,
    default=5,
    help="Threshold for maximum number of operators to keep at each iteration.",
)


def main():
    random.seed(0)

    args = parser.parse_args()

    # Load planning dataset.
    planning_problems = datasets.load_planning_problems_dataset(
        dataset_name=args.dataset_name,
        dataset_fraction=args.dataset_fraction,
        training_plans_fraction=args.training_plans_fraction,
        dataset_pddl_directory=args.dataset_pddl_directory,
        initial_pddl_operators=args.initial_pddl_operators,
        initial_plans_prefix=args.initial_plans_prefix,
        verbose=args.verbose,
    )
    # Load the PDDL domain definition.
    pddl_domain = datasets.load_pddl_domain(
        args.pddl_domain_name, args.initial_pddl_operators, args.verbose
    )
    # Load any external supervision on PDDL domains.
    supervision_pddl = datasets.load_pddl_supervision(
        supervision_name=args.supervision_name, verbose=args.verbose,
    )

    for curr_iteration in range(args.train_iterations):
        if not args.debug_no_propose_plans_operators_goals:
            # LLM proposal: propose plans, operators for plans, predicates for operators, and goals.
            codex.propose_plans_operators_goals_for_problems(
                pddl_domain,
                planning_problems["train"],
                supervision_pddl=supervision_pddl,
                n_samples=1,
                verbose=args.verbose,
                output_directory=args.output_directory,
                command_args=args,
            )
            # Preprocess the Codex proposals.
            pddl.preprocess_proposed_plans_operators_goals(
                pddl_domain,
                problems=planning_problems["train"],
                verbose=args.verbose,
                output_directory=args.output_directory,
                command_args=args,
            )

        # Task planner: evaluates costs with PDDL solver.
        task_planner.evaluate_task_plans_and_costs_for_problems(
            pddl_domain=pddl_domain,
            problems=planning_problems["train"],
            verbose=args.verbose,
            command_args=args,
            output_directory=args.output_directory,
            use_mock=args.debug_mock_task_plans,
        )
        # Motion planner: evaluate costs using motion planner.
        motion_planner.evaluate_motion_plans_and_costs_for_problems(
            curr_iteration=curr_iteration,
            pddl_domain=pddl_domain,
            problems=planning_problems["train"],
            verbose=args.verbose,
            command_args=args,
            output_directory=args.output_directory,
            use_mock=args.debug_mock_motion_plans,
            debug_skip=args.debug_skip_motion_plans,
            dataset_name=args.dataset_name,
        )

        # Update the domain definition based on operators in solved problems.
        pddl.update_pddl_domain_from_planner_results(
            pddl_domain=pddl_domain,
            problems=planning_problems["train"],
            top_n_operators=args.top_n_operators,
            verbose=args.verbose,
            command_args=args,
            output_directory=args.output_directory,
            dataset_name=args.dataset_name,
        )
        experiment_utils.output_iteration_summary(
            curr_iteration=curr_iteration,
            pddl_domain=pddl_domain,
            problems=planning_problems["train"],
            command_args=args,
            output_directory=args.output_directory,
        )

        # TODO: reset the proposed problem plans?
        # TODO: evaluate current progress.
        # Print some kind of output file showing 'how many problems were solved'.
        # Print some kind of summary file with the current best cleaned operator set.
    # Evaluate on heldout test sets.


if __name__ == "__main__":
    main()
