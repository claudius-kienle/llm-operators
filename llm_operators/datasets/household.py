#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import random
import json

import numpy as np

from llm_operators.datasets.dataset_core import (
    Problem,
    register_planning_pddl_domain,
    register_planning_domain_problems,
)
from llm_operators.datasets.dataset_utils import load_pddl_file_with_operators
from llm_operators.pddl import PDDLProblem


HOUSEHOLD_PDDL_DOMAIN_NAME = "household"

def load_household_pddl_file(
    dataset_pddl_directory, problem_directory
):
    with open(os.path.join(dataset_pddl_directory, problem_directory)) as f:
        problem_file = f.read()

    return problem_file


@register_planning_pddl_domain(HOUSEHOLD_PDDL_DOMAIN_NAME)
def load_household_pddl_domain(verbose=False):
    HOUSEHOLD_DOMAIN_FILE_PATH = "data/dataset/household/domain.pddl"
    domain = load_pddl_file_with_operators(
        domain_name=HOUSEHOLD_PDDL_DOMAIN_NAME,
        file_path=HOUSEHOLD_DOMAIN_FILE_PATH,
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




# Household Dataset.
HOUSEHOLD_DATASET_NAME = "household"
HOUSEHOLD_DATASET_PATH = "data/dataset/alfred-NLgoals-operators.json"

# Use the linearized problems
HOUSEHOLD_DEFAULT_PDDL_DIRECTORY = "data/dataset/household"


@register_planning_domain_problems(HOUSEHOLD_DATASET_NAME)
def load_household_planning_domain_problems(
    dataset_pddl_directory=HOUSEHOLD_DEFAULT_PDDL_DIRECTORY,
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
    with open(HOUSEHOLD_DATASET_PATH) as f:
        alfred_json = json.load(f)
    
    jsons = []
    for sample in (Path(dataset_pddl_directory) / "problems").glob("p*.pddl"):
        import re
        if re.match(r"p\d{2}\.pddl", sample.name) is None:
            continue
        problem_file = sample
        nl_problem = (sample.parent / (f"{sample.stem}.nl")).read_text()
        nl_goal = nl_problem.split("goal")
        assert len(nl_goal) == 2, f"Problem {problem_file} has no goal."
        nl_goal = "\n".join(nl_goal[1].strip().splitlines()[1:])

        actions = (sample.parent / (f"{sample.stem}-sample_plan.plan")).read_text().splitlines()
        acts = []
        for action in actions:
            stubs = action.strip()[1:-1].split(" ")
            action_name = stubs[0]
            action_args = stubs[1:]
            acts.append({
                "action": action_name,
                "args": action_args
            })
        jsons.append({
            "file_name": f"problems/{problem_file.name}",
            "goal": (sample.parent / (f"{sample.stem}-gt-goal.nl")).read_text().strip(),
            "operator_sequence": acts,
        })
    alfred_json = {
        "train": jsons,
        "valid_seen": [],
        "valid_unseen": [],
    }

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
                ground_truth_pddl_problem_string=load_household_pddl_file(
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
            new_problem.constants_in_problem_file = True
            dataset[dataset_split][problem_id] = new_problem

    if verbose:
        print(
            f"\nload_alfred_planning_domain_problems: loaded {HOUSEHOLD_DATASET_NAME} from {HOUSEHOLD_DATASET_PATH}"
        )
        for dataset_split in dataset:
            print(
                f"{dataset_split} : {len(dataset[dataset_split])} / original {len(alfred_json[dataset_split])} problems"
            )
    return dataset

