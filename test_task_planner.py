"""
test_task_planner.py
"""
import datasets
import pddl
import task_planner
from pddlgym_planners.ff import FF


def get_mock_pddl_domain():
    return datasets.load_alfred_pddl_domain()


def get_mock_problem():
    TEST_ALFRED_PDDL_PROBLEM_FILE = "dataset/alfred-sample-problem-0-0.pddl"
    with open(TEST_ALFRED_PDDL_PROBLEM_FILE) as f:
        test_problem_string = f.read()

    pddl_problem = pddl.PDDLProblem(
        ground_truth_pddl_problem_string=test_problem_string
    )
    problem = datasets.Problem(ground_truth_pddl_problem=pddl_problem)
    problem.proposed_pddl_goals = [pddl_problem.ground_truth_goal]
    return problem


def test_alfred_ff_planner():
    # Install with: https://github.com/askforalfred/alfred/tree/master/gen
    import alfred_gen.planner.ff_planner_handler as alfred_ff

    DOMAIN_FNAME = "domains/alfred.pddl"
    TEST_ALFRED_PDDL_PROBLEM_FILE = "dataset/alfred-sample-problem-0-0.pddl"
    plan_parser = alfred_ff.SinglePlanParser(domain_file_path=DOMAIN_FNAME)
    plan = plan_parser.get_plan_from_file(
        domain_path=DOMAIN_FNAME, filepath=TEST_ALFRED_PDDL_PROBLEM_FILE
    )
    import pdb

    pdb.set_trace()


def test_pddlgym_ff_planner():
    ff_planner = FF()
    DOMAIN_FNAME = "domains/alfred.pddl"
    TEST_ALFRED_PDDL_PROBLEM_FILE = "dataset/alfred-sample-problem-0-0.pddl"
    ff_planner.plan_from_pddl(
        dom_file=DOMAIN_FNAME, prob_file=TEST_ALFRED_PDDL_PROBLEM_FILE, timeout=2,
    )


def test_fd_plan():
    DOMAIN_FNAME = "domains/alfred.pddl"
    TEST_ALFRED_PDDL_PROBLEM_FILE = "dataset/alfred-sample-problem-0-0.pddl"
    success, out = task_planner.fd_plan(
        domain_fname=DOMAIN_FNAME, problem_fname=TEST_ALFRED_PDDL_PROBLEM_FILE
    )
    print(success)
    print(out)


def test_evaluate_task_plans_and_costs_for_problem():
    alfred_domain = get_mock_pddl_domain()
    alfred_problem = get_mock_problem()
    task_planner.evaluate_task_plans_and_costs_for_problem(
        pddl_domain=alfred_domain, problem=alfred_problem
    )
