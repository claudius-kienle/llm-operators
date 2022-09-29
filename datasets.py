"""
planning_domain.py | Classes for representing planning domains and planning domain datasets.
"""
import os
import random
import numpy as np
import json
from pddl import *

PDDL_PLAN = "pddl_plan"
PDDL_PLAN_OVERALL_COST = "pddl_plan_overall_cost"


class Problem:
    # A planning problem, which contains both PDDL and low-level plan information.
    def __init__(
        self,
        problem_id=None,
        dataset_split=None,
        language=None,
        ground_truth_pddl_plan=None,
        ground_truth_pddl_problem=None,
        should_supervise_pddl=False,
    ):
        self.problem_id = problem_id
        self.dataset_split = dataset_split

        self.language = language  # An NL string describing the planning problem.
        self.ground_truth_pddl_problem = (
            ground_truth_pddl_problem  # Ground truth PDDL problem object.
        )
        self.ground_truth_pddl_plan = PDDLPlan(
            plan=ground_truth_pddl_plan
        )  # A ground truth PDDLPlan object.

        self.should_supervise_pddl = (
            should_supervise_pddl  # Whether to include the PDDL in initial supervision
        )

        # One or more proposed PDDL goals.
        self.proposed_pddl_goals = []
        # One or more proposed plans. Array of PDDL {action, args} operator sequences.
        self.proposed_pddl_plans = []

        # Array of dicts containing solved PDDL plans and associated planning costs, evaluated by a symbolic planner. Created by the task planner.
        self.evaluated_pddl_plans = []

        # Array of dicts containing evaluated motion plans and associated planning costs, evaluated by a symbolic planner.
        self.evaluated_low_level_plans = []

    def get_best_evaluated_pddl_plan(self):
        return sorted(self.evaluated_pddl_plans, key=lambda p: p.overall_plan_cost)[0]

    def to_string(self):
        if self.pddl_problem is not None:
            return str(self.pddl_problem)
        else:
            assert False


######### PLANNING DOMAIN PDDL DOMAIN DEFINITION LOADERS.
PLANNING_PDDL_DOMAINS_REGISTRY = dict()


def register_planning_pddl_domain(name):
    def wrapper(f):
        PLANNING_PDDL_DOMAINS_REGISTRY[name] = f
        return f

    return wrapper


def load_pddl_domain(pddl_domain_name, initial_pddl_operators, verbose):
    planning_domain_loader = PLANNING_PDDL_DOMAINS_REGISTRY[pddl_domain_name]
    pddl_domain = planning_domain_loader(verbose)
    # Only keep the designated initial operators.
    for o in list(pddl_domain.operators.keys()):
        if o not in initial_pddl_operators:
            pddl_domain.remove_operator(o)
    if verbose:
        print("\nInitializing with operators: ")
        for o in list(pddl_domain.operators.keys()):
            print(o)
    return pddl_domain


# ALFRED Dataset.
ALFRED_PDDL_DOMAIN_NAME = "alfred"


@register_planning_pddl_domain(ALFRED_PDDL_DOMAIN_NAME)
def load_alfred_pddl_domain(verbose=False):
    ALFRED_DOMAIN_FILE_PATH = "domains/alfred.pddl"
    with open(os.path.join(ALFRED_DOMAIN_FILE_PATH)) as f:
        raw_pddl = f.read()
    domain = Domain(pddl_domain=raw_pddl)
    domain.ground_truth_operators = {
        o: copy.deepcopy(domain.operators[o]) for o in domain.operators
    }
    if verbose:
        print(
            f"\nload_alfred_pddl_domain: loaded {ALFRED_PDDL_DOMAIN_NAME } from {ALFRED_DOMAIN_FILE_PATH}"
        )
        print("\nGround truth operators: ")
        for o in list(domain.ground_truth_operators.keys()):
            print(o)
    return domain


######### PLANNING DOMAIN PROBLEM DATASET LOADERS.
PLANNING_PROBLEMS_REGISTRY = dict()


def register_planning_domain_problems(name):
    def wrapper(f):
        PLANNING_PROBLEMS_REGISTRY[name] = f
        return f

    return wrapper


def load_planning_problems_dataset(
    dataset_name, dataset_fraction, training_plans_fraction, verbose
):
    planning_domain_loader = PLANNING_PROBLEMS_REGISTRY[dataset_name]
    initial_planning_problems = planning_domain_loader(verbose)
    # Initialize some fraction of the dataset
    fraction_dataset = dict()
    for split in initial_planning_problems:
        fraction_dataset[split] = dict()
        num_to_take = int(
            np.ceil(dataset_fraction * len(initial_planning_problems[split]))
        )
        fraction_split = random.sample(
            list(initial_planning_problems[split].keys()), num_to_take
        )
        fraction_dataset[split] = {
            problem_id: initial_planning_problems[split][problem_id]
            for problem_id in fraction_split
        }

    # Initialize some fraction of the training problems for supervision. TODO (cw): maybe these shouldn't be random, but rather should have initial operators.
    train_split = "train"
    num_initial_plans = int(
        np.ceil(training_plans_fraction * len(fraction_dataset[train_split]))
    )
    initial_plans = random.sample(
        list(fraction_dataset[train_split].keys()), num_initial_plans
    )
    for problem in initial_plans:
        fraction_dataset[train_split][problem].should_supervise_pddl = True

    if verbose:
        print(f"dataset_fraction: {dataset_fraction}")
        for dataset_split in fraction_dataset:
            print(f"{dataset_split} : {len(fraction_dataset[dataset_split])} problems")
    return fraction_dataset


# ALFRED Dataset.
ALFRED_DATASET_NAME = "alfred"
ALFRED_DATASET_PATH = "dataset/alfred-NLgoals-operators.json"


@register_planning_domain_problems(ALFRED_DATASET_NAME)
def load_alfred_planning_domain_problems(verbose=False):
    """
    splits are: train, valid_seen, valid_unseen
    :ret: {
        split: {problem_id : Problem}
        }
    for the ALFRED dataset.
    """
    with open(ALFRED_DATASET_PATH) as f:
        alfred_json = json.load(f)

    dataset = dict()
    for dataset_split in alfred_json:
        dataset[dataset_split] = dict()
        for idx, problem_json in enumerate(alfred_json[dataset_split]):
            problem_id = f"{idx}_{problem_json['goal']}"
            goal_language = problem_json["goal"]
            ground_truth_pddl_plan = problem_json["operator_sequence"]
            new_problem = Problem(
                problem_id=problem_id,
                dataset_split=dataset_split,
                language=goal_language,
                ground_truth_pddl_plan=ground_truth_pddl_plan,
            )
            dataset[dataset_split][problem_id] = new_problem

    if verbose:
        print(
            f"\nload_alfred_planning_domain_problems: loaded {ALFRED_DATASET_NAME} from {ALFRED_DATASET_PATH}"
        )
        for dataset_split in dataset:
            print(f"{dataset_split} : {len(dataset[dataset_split])} problems")
    return dataset
