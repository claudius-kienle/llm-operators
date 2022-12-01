from pddl import PDDLProblem


def test_pddl_problem_alfred():
    TEST_ALFRED_PDDL_PROBLEM_FILE = "dataset/alfred-sample-problem-0-0.pddl"
    with open(TEST_ALFRED_PDDL_PROBLEM_FILE) as f:
        test_problem_string = f.read()

    pddl_problem = PDDLProblem(ground_truth_pddl_problem_string=test_problem_string)
    PROPOSED_GOAL = "(:goal test)"
    pddl_problem_string = pddl_problem.get_pddl_string_with_proposed_goal(
        proposed_goal=PROPOSED_GOAL
    )
    assert PROPOSED_GOAL in pddl_problem_string
    assert pddl_problem.ground_truth_goal not in PROPOSED_GOAL


def test_pddl_operator():
    test_operator = """(:action GotoLocation
        :parameters (?a - agent ?lStart - location ?lEnd - location)
        :precondition (and
            (atLocation ?a ?lStart)
            (forall
                (?re - receptacle)
                (not (opened ?re))
            )
        )
        :effect (and
            (atLocation ?a ?lEnd)
            (not (atLocation ?a ?lStart))
            (increase (totalCost) (distance ?lStart ?lEnd))
        )
    )"""
    from pddl_parser.pddl_parser import PDDL_Parser

    parser = PDDL_Parser()
    parser.parse_actions(pddl_string=test_operator)

