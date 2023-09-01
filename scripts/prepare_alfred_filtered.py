"""
prepare_alfred_filtered.py
Allows a human annotator to reject examples of goals based on the oracle goal check.

Rejection criteria:
1. Final location is missing from goal. Example: "get a knife to cut a tomato." - train/pick_and_place_simple-TomatoSliced-None-SinkBasin-5/trial_T20190907_233445_502551
2. Object is missing from goal: Example: "get the knife from the counter then open and close the fridge door." - train/pick_and_place_simple-TomatoSliced-None-Fridge-6/trial_T20190907_233305_019895
3. Key verb is entirely missing from goal, and cannot be inferred from the receptacle. "move cooked food to the kitchen table." - train/pick_heat_then_place_in_recep-BreadSliced-None-DiningTable-7/trial_T20190906_200122_168916 -- this is also an example of entirely missing the core specified object.
    "putting a tomato slice in the fridge." - train/pick_heat_then_place_in_recep-TomatoSliced-None-Fridge-14/trial_T20190911_114912_806806

3. Overspecification of goal (this might make it impossible to execute): Example: "to put a cooled plus sliced tomato on the table to the right of the fridge." - train/pick_and_place_simple-TomatoSliced-None-SideTable-3/trial_T20190908_091658_623792
4. 

Acceptable:
1. Any reasonable synonym for a location: Example: "place a chilled pan in the cupboard." - train/pick_cool_then_place_in_recep-Pan-None-Cabinet-18/trial_T20190907_222321_075263
2. Any reasonable synonym for a verb: Example: "put a microwaved egg in the garbage." -- train/pick_heat_then_place_in_recep-Egg-None-GarbageCan-8/trial_T20190909_120617_866099

"""
import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

import random

random.seed(0)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--raw_alfred_goal_file",
    type=str,
    default="data/dataset/alfred-cot-250-filtered-NLgoals-operators_raw.json",
    help="Original ALFRED file.",
)

parser.add_argument(
    "--output_alfred_goal_file",
    type=str,
    default="data/dataset/alfred-cot-250-filtered-NLgoals-operators.json",
    help="Original ALFRED file.",
)

def load_alfred_raw_goals_file(args):
    with open(args.raw_alfred_goal_file) as f:
        raw_goals = json.load(f)
    goal_type_to_goals = defaultdict(lambda: defaultdict(list))
    for split in raw_goals:
        for g in raw_goals[split]:
            goal_type_to_goals[split][g['goal_prefix']].append(g)
    
    for split in goal_type_to_goals:
        print(f"split: {split}")
        for goal_type in goal_type_to_goals[split]:
            print(f"{goal_type} : {len(goal_type_to_goals[split][goal_type])}")
    return goal_type_to_goals
def manually_filter_goals(args, goal_type_to_goals):
    filtered_goal_type_to_goals = defaultdict(lambda: defaultdict(list))
    rejected_goal_type_to_goals = defaultdict(lambda: defaultdict(list))
    for split in goal_type_to_goals:
        for goal_type in goal_type_to_goals[split]:
            for idx, goal in enumerate(goal_type_to_goals[split][goal_type]):
                print(f"{idx}: {goal['cot']}")

                i = ""
                while i not in ["y", "n"]:
                    i = input(f"{idx}: {goal['goal']}")
                category = filtered_goal_type_to_goals if i == "y" else rejected_goal_type_to_goals
                category[split][goal_type].append(goal)
                with open(args.output_alfred_goal_file + "_temp.json", "w") as f:
                    json.dump({
                        "accepted" : filtered_goal_type_to_goals,
                        "rejected" : rejected_goal_type_to_goals
                    }, f)

def main():
    args = parser.parse_args()
    alfred_nl_goal_type_to_goals = load_alfred_raw_goals_file(args)
    manually_filter_goals(args, alfred_nl_goal_type_to_goals)



if __name__ == "__main__":
    main()
