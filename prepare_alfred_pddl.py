"""
prepare_alfred_pddl.py | Author: zyzzyva@mit.edu.

This preparation script was used to create the modified ALFRED PDDL dataset that we use for planning. Modifies goals from: https://github.com/askforalfred/alfred/blob/master/gen/goal_library.py
"""
import argparse
import json
import os
import sys
from pddl import PDDLProblem
import task_planner
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument(
    "--pddl_domain_file",
    type=str,
    default="domains/alfred_linearized.pddl",
    help="Location of the original PDDL domain file.",
)
parser.add_argument(
    "--dataset_path",
    type=str,
    default="dataset/alfred_pddl",
    help="Location of the original PDDL dataset files.",
)
parser.add_argument(
    "--output_dataset_path",
    type=str,
    default="dataset/alfred_linearized_pddl",
    help="Location of the original PDDL dataset files.",
)
parser.add_argument(
    "--tasks_json",
    type=str,
    default="dataset/alfred-NLgoals-operators.json",
    help="Location of the JSON containing the original problems.",
)
parser.add_argument(
    "--skip_exists", action="store_true", help="If exists, skip it.",
)


def load_alfred_nl_goals(args):
    with open(args.tasks_json) as f:
        return json.load(f)


def get_goals_for_prefix(goal_prefix, goals):
    goals_for_prefix = []
    for goal in goals:
        curr_goal_prefix = goal.split("/")[1].split("-")[0]

        if curr_goal_prefix == "pick_and_place_simple":
            if curr_goal_prefix == goal_prefix and not "Sliced" in goal.split("/")[1]:
                goals_for_prefix.append(goal)
        else:
            if curr_goal_prefix == goal_prefix:
                goals_for_prefix.append(goal)
    return goals_for_prefix


def preprocess_problem_domain(args, goal_file, goal_data):
    goal_pddl_file = os.path.join(args.dataset_path, goal_file, "problem_0.pddl")

    print(goal_pddl_file)

    with open(goal_pddl_file) as f:
        problem_file = f.read()

    with open(args.pddl_domain_file) as f:
        domain_file = f.read()

    # Remove the cost predicate.
    problem_file = "\n".join(
        [l for l in problem_file.split("\n") if "totalCost" not in l]
    )

    # Remove the distance predicate.
    problem_file = "\n".join(
        [l for l in problem_file.split("\n") if "distance" not in l]
    )

    # Remove the canContain predicate.
    problem_file = "\n".join(
        [l for l in problem_file.split("\n") if "canContain" not in l]
    )

    # Dedup files.
    deduped_lines = []
    for l in problem_file.split("\n"):
        if "loc" in l:
            if l not in deduped_lines:
                deduped_lines.append(l)
        else:
            deduped_lines.append(l)
    problem_file = "\n".join(deduped_lines)

    return problem_file, domain_file


def write_preprocessed_file(args, goal_file, problem_string):
    output_pddl_file = os.path.join(args.output_dataset_path, goal_file)
    Path(output_pddl_file).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(output_pddl_file, "problem_0.pddl"), "w") as f:
        f.write(problem_string)


def preprocess_file_and_replace_goal(args, goal_file, goal_data, alternate_goal):
    problem_file, domain_file = preprocess_problem_domain(args, goal_file, goal_data)
    new_goal_pddl_file = os.path.join(
        args.output_dataset_path, goal_file, "problem_0.pddl"
    )
    if args.skip_exists and os.path.exists(new_goal_pddl_file):
        return

    problem = PDDLProblem(ground_truth_pddl_problem_string=problem_file)
    problem = problem.get_pddl_string_with_proposed_goal(alternate_goal)
    # Check that we can solve the modified version.
    solved, plan = task_planner.fd_plan_from_strings(domain_file, problem)
    if not solved:
        print(f"Error at: {goal_file}")
        print(solved, plan)
        sys.exit(0)
    write_preprocessed_file(args, goal_file, problem_string=problem)


def pick_and_place_simple(args, goal_file, goal_data):
    # Reparse the goal.
    curr_goal_prefix = goal_file.split("/")[1]
    goal_obj, goal_recep = (
        curr_goal_prefix.split("-")[1],
        curr_goal_prefix.split("-")[3],
    )
    alternate_goal = f"""
    (:goal
            (and 
                (objectType ?o {goal_obj}Type) 
                (receptacleType ?r {goal_recep}Type)
                (inReceptacle ?o ?r) 
            )
    )"""
    preprocess_file_and_replace_goal(args, goal_file, goal_data, alternate_goal)


def pick_clean_then_place_in_recep(args, goal_file, goal_data):
    # Reparse the goal.
    curr_goal_prefix = goal_file.split("/")[1]
    goal_obj, goal_recep = (
        curr_goal_prefix.split("-")[1],
        curr_goal_prefix.split("-")[3],
    )
    alternate_goal = f"""
    (:goal
            (and 
                (objectType ?o {goal_obj}Type) 
                (receptacleType ?r {goal_recep}Type)
                (inReceptacle ?o ?r)
                (cleanable ?o)
                (isClean ?o) 
            )
    )"""
    preprocess_file_and_replace_goal(args, goal_file, goal_data, alternate_goal)


GOAL_PREFIXES = {
    "pick_and_place_simple": pick_and_place_simple,
    "pick_clean_then_place_in_recep": pick_clean_then_place_in_recep,
}


def main():
    args = parser.parse_args()
    alfred_nl_goals = load_alfred_nl_goals(args)
    for split in alfred_nl_goals:
        print(f"Preparing split: {split} with {len(alfred_nl_goals[split])} tasks")
        goals = {goal["file_name"]: goal for goal in alfred_nl_goals[split]}
        for goal_prefix in GOAL_PREFIXES:
            goals_for_prefix = get_goals_for_prefix(goal_prefix, goals)
            print(f"Modifying {len(goals_for_prefix)} goals for {goal_prefix}")
            goal_modification_fn = GOAL_PREFIXES[goal_prefix]
            for goal in goals_for_prefix:
                goal_modification_fn(args, goal, goals[goal])

    # Pick and place simple sliced.

    #


if __name__ == "__main__":
    main()
