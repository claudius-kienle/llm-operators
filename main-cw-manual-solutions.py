#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path as osp
import sys
import argparse

import llm_operators.datasets as datasets
import llm_operators.experiment_utils as experiment_utils
import llm_operators.datasets.crafting_world as crafting_world
from llm_operators.datasets.crafting_world import CraftingWorld20230204Simulator, local_search_for_subgoal, SimpleConjunction

# Import Jacinle.
JACINLE_PATH = osp.join(osp.dirname(osp.abspath(__file__)), "../jacinle")
print("Adding jacinle path: {}".format(JACINLE_PATH))
sys.path.insert(0, JACINLE_PATH)

# Import Concepts.
CONCEPTS_PATH = osp.join(osp.dirname(osp.abspath(__file__)), "../concepts")
print("Adding concepts path: {}".format(CONCEPTS_PATH))
sys.path.insert(0, CONCEPTS_PATH)

crafting_world.SKIP_CRAFTING_LOCATION_CHECK = True
print('Skipping location check in Crafting World.')

import concepts.pdsketch as pds
from concepts.pdsketch.strips.strips_grounding_onthefly import OnTheFlyGStripsProblem, ogstrips_bind_arguments

ALL = 'ALL'


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--pddl_domain_name", type=str, help="Name of the PDDL domain to load.")
    parser.add_argument("--dataset_name", type=str, help="Name of the dataset of planning problems to load.")
    parser.add_argument("--dataset_fraction", default=1.0, type=float, help="Fraction of the overall dataset to work with. Lower than 1.0 for debugging purposes only.")
    parser.add_argument("--dataset_pddl_directory", type=str, help="Location of the top level PDDL directory.")

    # Mark the fraction of the dataset that we want to supervise on.
    parser.add_argument("--goal_supervision_fraction", default=0.1, type=float, help="Randomly selected fraction of the dataset to supervise with ground truth PDDL goals.")
    parser.add_argument("--initial_goal_supervision_prefix", type=str, nargs="+", default=[ALL], help="Which initial goal types to supervise on, or ALL if we want to sample ALL of the goal types. This will be sampled in accordance to the underlying distribution of problems of that problem type.")
    parser.add_argument("--plan_supervision_fraction", default=0.1, type=float, help="Randomly selected fraction of the dataset to supervise with ground truth PDDL goals.")
    parser.add_argument("--initial_plans_prefix", type=str, nargs="+", default=[ALL], help="Which initial plan types to supervise on. Used to seed the Codex proposals, or ALL if we want some subset of the initial")

    # Codex proposal parameters.
    parser.add_argument("--initial_pddl_predicates", type=str, nargs="+", default=[], help="Which initial PDDL predicates to run with.  Used to seed the Codex proposals.")
    parser.add_argument("--initial_pddl_operators", type=str, nargs="+", help="Which initial PDDL operators to run with.  Used to seed the Codex proposals.")
    parser.add_argument("--operator_propose_minimum_usage", type=int, default=2, help="Minimum number of times an operator must be used to be considered for proposal.")
    parser.add_argument('--operator-use-cot', type=int, default=1, help='whether to use cot for operator proposal: 1 for yes, 0 for no')
    parser.add_argument("--goal_propose_include_codex_types", action="store_true", help="Whether to include Codex types in the prompts for goal proposal.")

    parser.add_argument("--verbose", action="store_true", help="Whether to print out debugging information.")

    args = parser.parse_args()

    experiment_utils.hook_exception_ipdb()

    pddl_domain = datasets.load_pddl_domain(args.pddl_domain_name, args.initial_pddl_operators, args.verbose)
    # pddl_domain.init_operators_to_scores(args.operator_pseudocounts)

    # Load planning dataset.
    planning_problems = datasets.load_planning_problems_dataset(
        dataset_name=args.dataset_name,
        dataset_fraction=args.dataset_fraction,
        dataset_pddl_directory=args.dataset_pddl_directory,
        initial_goal_supervision_fraction=args.goal_supervision_fraction,
        initial_goal_supervision_prefix=args.initial_goal_supervision_prefix,
        initial_plan_supervision_fraction=args.plan_supervision_fraction,
        initial_plan_supervision_prefix=args.initial_plans_prefix,
        initial_pddl_operators=args.initial_pddl_operators,
        domain=pddl_domain,
        verbose=args.verbose,
    )

    current_domain_string = pddl_domain.to_string(
        ground_truth_operators=False,
        current_operators=True,
    )
    pds_domain = pds.load_domain_string(current_domain_string)

    # run_manual_solution_primitive(pds_domain, planning_problems['train'])
    # run_manual_solution_subgoal(pds_domain, planning_problems['train'])
    run_brute_force_search(pds_domain, planning_problems['train'])


def load_state_from_problem(pds_domain, problem_record, pddl_goal=None):
    pddl_problem = problem_record.ground_truth_pddl_problem
    current_problem_string = pddl_problem.get_ground_truth_pddl_string()
    problem = pds.load_problem_string(current_problem_string, pds_domain, return_tensor_state=False)

    gproblem = OnTheFlyGStripsProblem.from_domain_and_problem(pds_domain, problem)
    simulator = CraftingWorld20230204Simulator()
    simulator.reset_from_state(gproblem.objects, gproblem.initial_state)

    gt_goal = [x[1:-1] for x in pddl_problem.ground_truth_goal_list]

    return simulator, gt_goal


def run_manual_solution_primitive(pds_domain, problems):
    for problem_key, problem in problems.items():
        print('Now solving problem: {}'.format(problem_key))
        simulator, gt_goal = load_state_from_problem(pds_domain, problem)

        succ = True
        for action in problem.ground_truth_primitive_plan:
            print('  Action: {}'.format(action))
            rv = getattr(simulator, action['action'])(*action['args'])
            if not rv:
                print('    Failed to execute action: {}'.format(action))
                succ = False
                break

        if succ:
            succ = simulator.goal_satisfied(gt_goal)

        if not succ:
            print('  Failed to solve problem: {}'.format(problem_key))
            print('  Goal: {}'.format(gt_goal))
            from IPython import embed; embed();
            raise ValueError()

        print('Success: {}'.format(succ))


def run_manual_solution_subgoal(pds_domain, problems):
    for problem_key, problem in problems.items():
        print('Now solving problem: {}'.format(problem_key))
        simulator, gt_goal = load_state_from_problem(pds_domain, problem)

        succ = True
        for subgoal in problem.ground_truth_subgoal_sequence:
            print('  Subgoal: {}'.format(subgoal))
            rv = local_search_for_subgoal(simulator, SimpleConjunction(subgoal))
            if rv is None:
                print('    Failed to achieve subgoal: {}'.format(subgoal))
                succ = False
                break
            simulator, _ = rv

        if succ:
            succ = simulator.goal_satisfied(gt_goal)

        if not succ:
            print('  Failed to solve problem: {}'.format(problem_key))
            print('  Goal: {}'.format(gt_goal))
            from IPython import embed; embed();
            raise ValueError()

        print('Success: {}'.format(succ))


def run_brute_force_search(pds_domain, problems):
    for problem_key, problem in problems.items():
        print('Now solving problem: {}'.format(problem_key))
        simulator, gt_goal = load_state_from_problem(pds_domain, problem)
        rv = local_search_for_subgoal(simulator, SimpleConjunction(gt_goal))
        if rv is None:
            print('  Failed to solve problem: {}'.format(problem_key))
            print('  Goal: {}'.format(gt_goal))
        else:
            simulator, _ = rv
            succ = simulator.goal_satisfied(gt_goal)
            print('Success: {}'.format(succ))


if __name__ == '__main__':
    main()

