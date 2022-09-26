"""
main.py

Usage:  
    # Load a debug fraction of the ALFRED dataset.
    python main.py --dataset_name alfred --pddl_domain_name alfred --dataset_fraction 0.001 --training_plans_fraction 0.1 --initial_pddl_operators GotoLocation OpenObject  --verbose
--train_iterations 1
"""
import argparse
import random
import codex
import planning_domain


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
    "--pddl_domain_name", type=str, help="Name of the PDDL domain to load.",
)
parser.add_argument(
    "--initial_pddl_operators",
    type=str,
    nargs="+",
    help="Which initial PDDL operators to run with.  Used to seed the Codex proposals.",
)
parser.add_argument(
    "--train_iterations", type=int, help="How many training iterations to run.."
)
parser.add_argument("--verbose", action="store_true", help="Run on verbose.")


def main():
    random.seed(0)

    args = parser.parse_args()

    # Load planning problems and PDDL domain.
    planning_problems = planning_domain.load_planning_problems_dataset(
        args.dataset_name,
        args.dataset_fraction,
        args.training_plans_fraction,
        args.verbose,
    )
    pddl_domain = planning_domain.load_pddl_domain(
        args.pddl_domain_name, args.initial_pddl_operators, args.verbose
    )

    for curr_iteration in range(args.train_iterations):
        # Propose new operator definitions and plans.
        (
            proposed_codex_plans,
            proposed_codex_operators,
        ) = codex.propose_operators_for_problems(
            pddl_domain, planning_problems["train"], n_samples=1, verbose=args.verbose
        )

        # TODO: verify with high-level planner.

        # TODO: verify with low-level planner.

        # TODO: update domain.

        # TODO: evaluate.


if __name__ == "__main__":
    main()
