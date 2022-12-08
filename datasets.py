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
        goal_prefix=None,
    ):
        self.problem_id = problem_id
        self.dataset_split = dataset_split
        self.goal_prefix = goal_prefix

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

        # Evaluated PDDL plans that solve proposed_pddl_goals, created by a task planner.
        # This is a dict from {goal : PDDLPlan}
        self.evaluated_pddl_plans = {}

        # Array of dicts containing evaluated motion plans and associated planning costs, evaluated by a symbolic planner.
        self.evaluated_low_level_plans = []

    def get_best_evaluated_pddl_plan(self):
        return sorted(self.evaluated_pddl_plans, key=lambda p: p.overall_plan_cost)[0]

    def __repr__(self):
        return (
            "Problem(\n"
            "problem_id={},\n"
            "language={},\n"
            "should_supervise_pddl={}\n"
            "proposed_pddl_goals = {}\n"
            "proposed_pddl_plans = {}\n)\n".format(
                self.problem_id,
                self.language,
                self.should_supervise_pddl,
                self.proposed_pddl_goals,
                self.proposed_pddl_plans,
            )
        )


### Load supervision on external PDDL domains.
def load_pddl_supervision(supervision_name, verbose=False):
    # Load the supervision goals and operators. These should be in dataset/<supervision_name>-NLgoals-operators.json
    if supervision_name is None:
        return []
    with open(f"dataset/{supervision_name}-NLgoals-operators.json") as f:
        pddl_supervision = {goal["domain_file"]: goal for goal in json.load(f)}

    # Load natural language for these.  These should be in dataset/<supervision_name>-NL.json
    with open(f"dataset/{supervision_name}-NL.json") as f:
        for nl_goal in json.load(f):
            if nl_goal["domain_file"] in pddl_supervision:
                pddl_supervision[nl_goal["domain_file"]]["NL_goal"] = nl_goal["NL_goal"]

    for domain_file in list(pddl_supervision.keys()):
        if "NL_goal" not in pddl_supervision[domain_file]:
            del pddl_supervision[domain_file]
    if verbose:
        print("load_pddl_supervision from the following domain files:")
        for domain_file in pddl_supervision:
            print(domain_file)

    return pddl_supervision


######### PLANNING DOMAIN PDDL DOMAIN DEFINITION LOADERS.
# Planning domains available for the --dataset_name flag.
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
ALFWORLD_PDDL_DOMAIN_NAME = "alfworld"
ALFRED_LINEARIZED_PDDL_DOMAIN_NAME = "alfred_linearized"


def load_pddl_file_with_operators(domain_name, file_path, verbose=False):
    with open(os.path.join(file_path)) as f:
        raw_pddl = f.read()
    domain = Domain(pddl_domain=raw_pddl)
    domain.ground_truth_operators = {
        o: copy.deepcopy(domain.operators[o]) for o in domain.operators
    }
    domain.ground_truth_predicates = []
    if verbose:
        print(f"\nload_pddl_file_with_operators: loaded {domain_name} from {file_path}")
        print("\nGround truth operators: ")
        for o in list(domain.ground_truth_operators.keys()):
            print(o)
    return domain


@register_planning_pddl_domain(ALFRED_PDDL_DOMAIN_NAME)
def load_alfred_pddl_domain(verbose=False):
    ALFRED_DOMAIN_FILE_PATH = "domains/alfred.pddl"
    domain = load_pddl_file_with_operators(
        domain_name=ALFRED_PDDL_DOMAIN_NAME,
        file_path=ALFRED_DOMAIN_FILE_PATH,
        verbose=verbose,
    )
    # Remove the functions from the file and from all of the operators.
    domain.functions = ""

    def remove_functions(operator_body):
        return "\n".join([l for l in operator_body.split("\n") if "totalCost" not in l])

    for operator in domain.ground_truth_operators:
        operator_body = domain.ground_truth_operators[operator]
        domain.ground_truth_operators[operator] = remove_functions(operator_body)
    for operator in domain.operators:
        operator_body = domain.operators[operator]
        domain.operators[operator] = remove_functions(operator_body)
    return domain


@register_planning_pddl_domain(ALFWORLD_PDDL_DOMAIN_NAME)
def load_alfworld_pddl_domain(verbose=False):
    ALFWORLD_DOMAIN_FILE_PATH = "domains/alfworld.pddl"
    return load_pddl_file_with_operators(
        domain_name=ALFWORLD_PDDL_DOMAIN_NAME,
        file_path=ALFWORLD_DOMAIN_FILE_PATH,
        verbose=verbose,
    )


@register_planning_pddl_domain(ALFRED_LINEARIZED_PDDL_DOMAIN_NAME)
def load_alfworld_pddl_domain(verbose=False):
    ALFRED_LINEARIZED_PDDL_FILE_PATH = "domains/alfred_linearized.pddl"
    return load_pddl_file_with_operators(
        domain_name=ALFRED_LINEARIZED_PDDL_DOMAIN_NAME,
        file_path=ALFRED_LINEARIZED_PDDL_FILE_PATH,
        verbose=verbose,
    )


######### PLANNING DOMAIN PROBLEM DATASET LOADERS.
PLANNING_PROBLEMS_REGISTRY = dict()


def register_planning_domain_problems(name):
    def wrapper(f):
        PLANNING_PROBLEMS_REGISTRY[name] = f
        return f

    return wrapper


def get_problem_ids_with_ground_truth_operators(
    initial_pddl_operators, planning_dataset, split="train"
):
    """
    :ret: list of problem IDs where the ground truth plans contain these operators.
    """
    problem_ids = []
    initial_pddl_operators = set(initial_pddl_operators)
    for problem_id in planning_dataset[split]:
        problem = planning_dataset[split][problem_id]
        ground_truth_operators = set(
            [
                operator[PDDLPlan.PDDL_ACTION]
                for operator in problem.ground_truth_pddl_plan.plan
            ]
        )
        # Check that this plan doesn't contain any more operators than the initial ones.
        if len(initial_pddl_operators.union(ground_truth_operators)) <= len(
            initial_pddl_operators
        ):
            problem_ids.append(problem_id)
    return problem_ids


def get_problem_ids_with_initial_plans_prefix(
    initial_plans_prefix, planning_dataset, split="train"
):
    """
    :ret: list of problem IDs where the ground truth plans contain these operators.
    """
    problem_ids = []
    for problem_id in planning_dataset[split]:
        problem = planning_dataset[split][problem_id]
        if problem.goal_prefix in initial_plans_prefix:
            problem_ids.append(problem_id)
    return problem_ids


def load_planning_problems_dataset(
    dataset_name,
    dataset_fraction,
    training_plans_fraction,
    dataset_pddl_directory,
    initial_pddl_operators,
    initial_plans_prefix=None,
    verbose=False,
):
    planning_domain_loader = PLANNING_PROBLEMS_REGISTRY[dataset_name]
    # Load some fraction of the dataset.

    planning_dataset = planning_domain_loader(
        dataset_pddl_directory=dataset_pddl_directory,
        dataset_fraction=dataset_fraction,
        verbose=verbose,
    )

    if initial_plans_prefix:
        candidate_training_plans = get_problem_ids_with_initial_plans_prefix(
            initial_plans_prefix, planning_dataset, split="train"
        )
    else:
        # Get candidate problems to supervise on.
        candidate_training_plans = get_problem_ids_with_ground_truth_operators(
            initial_pddl_operators, planning_dataset, split="train"
        )
    # Supervise on a maximum of the training plans fraction.
    num_to_supervise = min(
        int(np.ceil(training_plans_fraction * len(planning_dataset["train"]))),
        len(candidate_training_plans),
    )
    problems_to_supervise = random.sample(candidate_training_plans, num_to_supervise,)
    if verbose:
        print("Supervising on these problems: ")
        print(problems_to_supervise)
    for problem_id in problems_to_supervise:
        planning_dataset["train"][problem_id].should_supervise_pddl = True

    if verbose:
        print(f"training_plans_fraction: {training_plans_fraction}")
        print(f"supervising on: {num_to_supervise} problems.")
    return planning_dataset


# ALFRED Dataset.
ALFRED_DATASET_NAME = "alfred"
ALFRED_DATASET_PATH = "dataset/alfred-NLgoals-operators.json"

# Development subset of 100 learning problems.
ALFRED_LINEARIZED_100_DATASET_NAME = "alfred_linearized_100"
ALFRED_LINEARIZED_100_DATASET_PATH = (
    "dataset/alfred-linearized-100-NLgoals-operators.json"
)


def load_alfred_pddl_file(
    dataset_pddl_directory, problem_directory, pddl_file="problem_0.pddl"
):

    with open(os.path.join(dataset_pddl_directory, problem_directory, pddl_file)) as f:
        problem_file = f.read()

    return problem_file


# Use the linearized problems
ALFRED_DEFAULT_PDDL_DIRECTORY = "dataset/alfred_linearized_pddl"


@register_planning_domain_problems(ALFRED_LINEARIZED_100_DATASET_NAME)
def load_alfred_linearized_planning_domain_problems(
    dataset_pddl_directory=ALFRED_DEFAULT_PDDL_DIRECTORY,
    dataset_fraction=1.0,
    verbose=False,
):
    """
    splits are: train, valid_seen, valid_unseen
    :ret: {
        split: {problem_id : Problem}
        }
    for the ALFRED dataset.
    """
    # Location of the local alfred-NLgoals-operators JSON.
    with open(ALFRED_LINEARIZED_100_DATASET_PATH) as f:
        alfred_json = json.load(f)

    dataset = dict()
    for dataset_split in alfred_json:
        dataset[dataset_split] = dict()
        # Get some fraction of the dataset to load.
        num_to_take = int(np.ceil(dataset_fraction * len(alfred_json[dataset_split])))
        fraction_split = random.sample(list(alfred_json[dataset_split]), num_to_take)
        for problem_json in fraction_split:
            problem_id = problem_json["file_name"]
            goal_language = problem_json["goal"]
            ground_truth_pddl_plan = problem_json["operator_sequence"]
            goal_prefix = (
                problem_json["goal_prefix"] if "goal_prefix" in problem_json else ""
            )

            ground_truth_pddl_problem = PDDLProblem(
                ground_truth_pddl_problem_string=load_alfred_pddl_file(
                    dataset_pddl_directory, problem_json["file_name"]
                )
            )
            new_problem = Problem(
                problem_id=problem_id,
                dataset_split=dataset_split,
                language=goal_language,
                ground_truth_pddl_plan=ground_truth_pddl_plan,
                ground_truth_pddl_problem=ground_truth_pddl_problem,
                goal_prefix=goal_prefix,
            )
            dataset[dataset_split][problem_id] = new_problem

    if verbose:
        print(
            f"\nload_alfred_planning_domain_problems: loaded {ALFRED_DATASET_NAME} from {ALFRED_DATASET_PATH}"
        )
        for dataset_split in dataset:
            print(
                f"{dataset_split} : {len(dataset[dataset_split])} / original {len(alfred_json[dataset_split])} problems"
            )
    return dataset


# Use the linearized problems
ALFRED_DEFAULT_PDDL_DIRECTORY = "dataset/alfred_linearized_pddl"


@register_planning_domain_problems(ALFRED_DATASET_NAME)
def load_alfred_planning_domain_problems(
    dataset_pddl_directory=ALFRED_DEFAULT_PDDL_DIRECTORY,
    dataset_fraction=1.0,
    verbose=False,
):
    """
    splits are: train, valid_seen, valid_unseen
    :ret: {
        split: {problem_id : Problem}
        }
    for the ALFRED dataset.
    """
    # Location of the local alfred-NLgoals-operators JSON.
    with open(ALFRED_DATASET_PATH) as f:
        alfred_json = json.load(f)

    dataset = dict()
    for dataset_split in alfred_json:
        dataset[dataset_split] = dict()
        # Get some fraction of the dataset to load.
        num_to_take = int(np.ceil(dataset_fraction * len(alfred_json[dataset_split])))
        fraction_split = random.sample(list(alfred_json[dataset_split]), num_to_take)
        for problem_json in fraction_split:
            problem_id = problem_json["file_name"]
            goal_language = problem_json["goal"]
            ground_truth_pddl_plan = problem_json["operator_sequence"]
            ground_truth_pddl_problem = PDDLProblem(
                ground_truth_pddl_problem_string=load_alfred_pddl_file(
                    dataset_pddl_directory, problem_json["file_name"]
                )
            )
            new_problem = Problem(
                problem_id=problem_id,
                dataset_split=dataset_split,
                language=goal_language,
                ground_truth_pddl_plan=ground_truth_pddl_plan,
                ground_truth_pddl_problem=ground_truth_pddl_problem,
            )
            dataset[dataset_split][problem_id] = new_problem

    if verbose:
        print(
            f"\nload_alfred_planning_domain_problems: loaded {ALFRED_DATASET_NAME} from {ALFRED_DATASET_PATH}"
        )
        for dataset_split in dataset:
            print(
                f"{dataset_split} : {len(dataset[dataset_split])} / original {len(alfred_json[dataset_split])} problems"
            )
    return dataset
