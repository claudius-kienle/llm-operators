"""
planning_domain.py | Classes for representing planning domains and planning domain datasets.
"""
import random
import numpy as np
import json


class Problem:
    # A planning problem.
    def __init__(
        self,
        problem_id=None,
        dataset_split=None,
        language=None,
        pddl_goal=None,
        pddl_initial_conditions=None,
        pddl_problem=None,
        pddl_plan=None,
        low_level_plan=None,
        ground_truth_pddl_plan=None,
    ):
        self.problem_id = problem_id
        self.dataset_split = dataset_split
        self.language = language  # A string describing the planning problem.
        self.pddl_goal = pddl_goal  # A string PDDL goal.
        self.pddl_initial_conditions = (
            pddl_initial_conditions  # String PDDL conditions.
        )
        self.pddl_problem = pddl_problem  # A string PDDL problem.
        self.pddl_plan = pddl_plan  # A solved PDDL plan. Array of PDDL {action, args} operator sequences.
        self.low_level_plan = low_level_plan

        # A proposed plan. Array of PDDL {action, args} operator sequences.
        self.proposed_pddl_plan = []

        # A ground truth plan. Array of PDDL {action, args} operator sequences.
        self.ground_truth_pddl_plan = ground_truth_pddl_plan

    def to_string(self):
        if self.pddl_problem is not None:
            return str(self.pddl_problem)
        else:
            assert False


######### PLANNING DOMAIN DATASET LOADERS.
PLANNING_PROBLEMS_REGISTRY = dict()


def register_planning_domain_problems(name):
    def wrapper(f):
        PLANNING_PROBLEMS_REGISTRY[name] = f
        return f

    return wrapper


def load_planning_problems_dataset(dataset_name, dataset_fraction, verbose):
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
            f"load_alfred_planning_domain_problems: loaded {ALFRED_DATASET_NAME} from {ALFRED_DATASET_PATH}"
        )
        for dataset_split in dataset:
            print(f"{dataset_split} : {len(dataset[dataset_split])} problems")
    return dataset
