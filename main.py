"""
main.py

Usage:  
    # Load a debug fraction of the ALFRED dataset.
    python main.py --dataset_name alfred --pddl_domain_name alfworld --dataset_fraction 0.001 --training_plans_fraction 0.1 --initial_pddl_operators GotoLocation PickupObject PutObject  --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_pddl --output_directory generated/test_outputs
"""
import argparse
import random
import codex
import datasets
from task_planner import evaluate_task_plans_and_costs_for_problems


parser = argparse.ArgumentParser()
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
    "--output_directory",
    type=str,
    help="Location of the directory for writing outputs.",
)
parser.add_argument("--verbose", action="store_true", help="Run on verbose.")
parser.add_argument(
    "--debug_no_propose_plans_operators_goals",
    action="store_true",
    help="debug: don't run propose_plans_operators_goals.",
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
        verbose=args.verbose,
    )
    # Load the PDDL domain definition.
    pddl_domain = datasets.load_pddl_domain(
        args.pddl_domain_name, args.initial_pddl_operators, args.verbose
    )

    for curr_iteration in range(args.train_iterations):
        if not args.debug_no_propose_plans_operators_goals:
            # LLM proposal: propose plans, operators for plans, predicates for operators, and goals.
            codex.propose_plans_operators_goals_for_problems(
                pddl_domain,
                planning_problems["train"],
                n_samples=1,
                verbose=args.verbose,
                output_directory=args.output_directory,
                command_args=args,
            )

        evaluate_task_plans_and_costs_for_problems(
            pddl_domain, planning_problems["train"]
        )

        # TODO: evaluate costs with low-level planner.

        # TODO: update domain
        # implementing in pddl currently
        # Update operators - assign scores based on how often they were used in successful plans.
        successful_plans = run_planner() # this updates problem objects in planning_problems in field evaluated_pddl_plans
        for plan in successful_plans: # a plan in a PDDLplan object, found in pddl.py
            update_domain(plan,n_ops) # +1 every time an action appears.n_ops is how many ops to take
        # Move successful operators from 'proposed' into the domain.
        # Update goals.

        # TODO: evaluate current progress.
        # Print some kind of output file showing 'how many problems were solved'.


if __name__ == "__main__":
    main()
