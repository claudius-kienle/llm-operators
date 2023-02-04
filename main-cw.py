#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import llm_operators.codex as codex
from llm_operators.datasets import load_pddl_domain, load_planning_problems_dataset

parser = argparse.ArgumentParser()
parser.add_argument("--experiment_name", type=str, default="", help="Experiment name tag. This will be appended to any checkpointed data.")
parser.add_argument("--dataset_name", type=str, help="Name of the dataset of planning problems to load." )
parser.add_argument("--dataset_fraction", default=1.0, type=float, help="Fraction of the overall dataset to work with. Lower than 1.0 for debugging purposes")
parser.add_argument("--training_plans_fraction", default=1.0, type=float, help="Fraction of the training problems to initialize with plans. Used to seed the Codex proposals.")
parser.add_argument("--dataset_pddl_directory", type=str, help="Location of the top level PDDL directory.")
parser.add_argument("--pddl_domain_name", type=str, help="Name of the PDDL domain to load.")
parser.add_argument("--train_iterations", type=int, help="How many training iterations to run." )
parser.add_argument("--supervision_name", type=str, default="supervision", help="Tag for the supervision dataset to load.")
parser.add_argument("--initial_plans_prefix", type=str, nargs="+", help="Which initial plan types to supervise on. Used to seed the Codex proposals")
parser.add_argument("--initial_pddl_operators", type=str, nargs="+", help="Which initial PDDL operators to run with.  Used to seed the Codex proposals.")
parser.add_argument("--initial_pddl_predicates", type=str, nargs="+", default=[], help="Which initial PDDL predicates to run with.  Used to seed the Codex proposals.")
parser.add_argument("--planner", type=str, default="fd", help="Which planner to use.")
parser.add_argument("--output_directory", type=str, help="Location of the directory for writing outputs.")
parser.add_argument("--verbose", action="store_true", help="Run on verbose.")
parser.add_argument("--debug_no_propose_plans_operators_goals", action="store_true", help="debug: don't run propose_plans_operators_goals. Instead, use ground truths.")
parser.add_argument("--debug_mock_propose_plans", action="store_true", help="debug: mock out plan proposal.")
parser.add_argument("--debug_mock_propose_operators", action="store_true", help="debug: mock out operator_proposal.")
parser.add_argument("--debug_mock_propose_goals", action="store_true", help="debug: mock out goal_proposal.")
parser.add_argument("--debug_mock_task_plans", action="store_true", help="debug: mock out task plan symbolic search.")
parser.add_argument("--debug_mock_motion_plans", action="store_true", help="debug: mock out motion plan grounded search.")
parser.add_argument("--debug_skip_motion_plans", action="store_true", help="debug: skip motion plan grounded search and assume that all of the task plans succeeded.")
parser.add_argument("--debug_ground_truth_operators", action="store_true", help="debug: use ground_truth_operators.")
parser.add_argument("--debug_ground_truth_goals", action="store_true", help="debug: use ground_truth_goals.")
parser.add_argument("--codex_goal_temperature", type=float, default=codex.DEFAULT_GOAL_TEMPERATURE, help="OpenAI temperature for goal proposal.")
parser.add_argument("--top_n_operators", type=int, default=5, help="Threshold for maximum number of operators to keep at each iteration.")


def main():
    args = parser.parse_args()
    planning_domain = load_pddl_domain(args.pddl_domain_name, args.initial_pddl_operators, verbose=True)

    # Load planning dataset.
    # $ python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place_1_13_2023 --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized
    # --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle
    # --verbose --train_iterations 1
    # --dataset_pddl_directory data/dataset/alfred_linearized_pddl --output_directory generated
    # --debug_mock_propose_plans --debug_mock_propose_operators --debug_mock_propose_goals

    planning_problems = load_planning_problems_dataset(
        dataset_name='alfred_linearized_100',
        dataset_fraction=1.0,
        training_plans_fraction=1.0,
        dataset_pddl_directory='data/dataset/alfred_linearized_pddl',
        initial_pddl_operators=['GotoLocation', 'PickupObjectInReceptacle', 'PickupObjectNotInReceptacle', 'PutObjectInReceptacle', 'PutReceptacleObjectInReceptacle'],
        initial_plans_prefix='pick_and_place_simple',
        verbose=args.verbose,
    )

    from llm_operators.datasets.alfred import load_alfred_linearized_planning_domain_problems
    planning_problems_inner = load_alfred_linearized_planning_domain_problems(
        'data/dataset/alfred_linearized_pddl',
        1.0
    )

    print(planning_domain)
    from IPython import embed; embed()


if __name__ == "__main__":
    main()
