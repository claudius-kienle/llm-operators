"""
main.py

Usage:  
    # Load a debug fraction of the ALFRED dataset.
    python main.py --dataset_name alfred --dataset_fraction 0.001 --verbose
"""
import argparse
import random
import planning_domain


parser = argparse.ArgumentParser()
parser.add_argument(
    "--dataset_name", type=str, help="Name of the dataset of planning problems to load."
)
parser.add_argument(
    "--dataset_fraction",
    default=1.0,
    type=float,
    help="Fraction of the dataset to work with.",
)
parser.add_argument(
    "--pddl_domain_name", type=str, help="Name of the PDDL domain to load.",
)
parser.add_argument(
    "--initial_pddl_operators",
    type=str,
    nargs="+",
    help="Which initial PDDL operators to run with.",
)
parser.add_argument("--verbose", action="store_true", help="Run on verbose.")


def main():
    random.seed(0)

    args = parser.parse_args()

    # Initialize planning domain.
    planning_problems = planning_domain.load_planning_problems_dataset(
        args.dataset_name, args.dataset_fraction, args.verbose
    )


if __name__ == "__main__":
    main()
