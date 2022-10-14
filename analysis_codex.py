from pddl import *
from codex import *
from datasets import *
import csv

###############################################################
# Here we write basic analysis functions to gain some insight #
# about how well codex is performing                          #
###############################################################


path = "alfred_data/"  # where to save csv files
dataset_name = "alfred"
dataset_fraction = 0.001
dataset_pddl_directory = "dataset/alfred_pddl"
pddl_domain_name = "alfred"
initial_pddl_operators = "GotoLocation OpenObject"
verbose = False

# Load dataset.
load_problems = datasets.load_planning_problems_dataset(
    dataset_name=dataset_name,
    dataset_fraction=dataset_fraction,
    dataset_pddl_directory=dataset_pddl_directory,
    training_plans_fraction=1,
    verbose=False
)

problems = list(load_problems["train"].values())
n = len(problems)

solved_problems = problems[:n//2]
unsolved_problems = problems[n//2:]

# Load the PDDL domain definition.
pddl_domain = datasets.load_pddl_domain(
    pddl_domain_name, initial_pddl_operators,verbose = False)

ground_truth_vs_proposed_goals = {}
# key is problem id, values are a list of 2 - ground truth goal and proposed

propose_PDDL_goals_for_problems(unsolved_problems, solved_problems, pddl_domain)

for problem in unsolved_problems:
    problem_id = problem.problem_id
    ground_truth = problem.ground_truth_pddl_problem.ground_truth_goal
    proposed_goal = problem.proposed_pddl_goals[0]
    ground_truth_vs_proposed_goals[problem_id] = [ground_truth, proposed_goal]

with open('alfred_data/ground_truth_vs_proposed_goals_new.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in ground_truth_vs_proposed_goals.items():
        writer.writerow([key, value[0],value[1]])
