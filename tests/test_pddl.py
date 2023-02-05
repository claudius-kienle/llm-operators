from llm_operators.pddl import Domain, OtherDomain, PDDLProblem


def test_pddl_problem_alfred():
    TEST_ALFRED_PDDL_PROBLEM_FILE = "data/dataset/alfred-sample-problem-0-0.pddl"
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
    from llm_operators.pddl_parser.pddl_parser import PDDL_Parser

    parser = PDDL_Parser()
    parser.parse_actions(pddl_string=test_operator)


def test_parse_problem_objects_pddl():
    TEST_PDDL_PROBLEM_FILE = "data/domains/supervision_domains/barman_problem_0.pddl"
    with open(TEST_PDDL_PROBLEM_FILE) as f:
        test_problem_string = f.read()
    pddl_problem = PDDLProblem(ground_truth_pddl_problem_string=test_problem_string)
    objects = ['shaker1', 'left', 'right', 'shot1', 'shot2', 'shot3', 'shot4', 'shot5', 'shot6', 'shot7',
               'shot8', 'shot9', 'shot10', 'shot11', 'shot12', 'shot13', 'shot14', 'shot15', 'shot16', 'shot17',
               'shot18', 'shot19', 'shot20', 'shot21', 'shot22', 'shot23', 'shot24', 'shot25', 'ingredient1',
               'ingredient2', 'ingredient3', 'ingredient4', 'ingredient5', 'ingredient6', 'ingredient7', 'ingredient8',
               'ingredient9', 'ingredient10', 'cocktail1', 'cocktail2', 'cocktail3', 'cocktail4', 'cocktail5',
               'cocktail6', 'cocktail7', 'cocktail8', 'cocktail9', 'cocktail10', 'cocktail11', 'cocktail12', 'cocktail13',
               'cocktail14', 'cocktail15', 'cocktail16', 'cocktail17', 'cocktail18', 'cocktail19', 'cocktail20',
               'cocktail21', 'cocktail22', 'cocktail23', 'cocktail24', 'dispenser1', 'dispenser2', 'dispenser3',
               'dispenser4', 'dispenser5', 'dispenser6', 'dispenser7', 'dispenser8', 'dispenser9', 'dispenser10',
               'level0', 'level1', 'level2']

    assert pddl_problem.parse_problem_objects_pddl() == objects


def test_parse_problem_objects_alfred():
    TEST_PDDL_PROBLEM_FILE = "data/dataset/alfred-sample-problem-0-0.pddl"
    with open(TEST_PDDL_PROBLEM_FILE) as f:
        test_problem_string = f.read()
    pddl_problem = PDDLProblem(ground_truth_pddl_problem_string=test_problem_string)
    return pddl_problem.parse_problem_objects_alfred()


def test_parse_goal_for_prompting():
    TEST_PDDL_PROBLEM_FILE = "data/dataset/alfred-sample-problem-0-0.pddl"
    with open(TEST_PDDL_PROBLEM_FILE) as f:
        test_problem_string = f.read()
    pddl_problem = PDDLProblem(ground_truth_pddl_problem_string=test_problem_string)
    return pddl_problem.parse_goal_for_prompting()


def test_OtherDomain_for_goal_prompting():
    TEST_DOMAIN_OTHER = "data/domains/supervision_domains/movie_domain.pddl"
    with open(TEST_DOMAIN_OTHER) as g:
        other_domain = OtherDomain(pddl_domain=g.read())
    TEST_PDDL_PROBLEM_FILE = "data/domains/supervision_domains/movie_problem_0.pddl"
    with open(TEST_PDDL_PROBLEM_FILE) as f:
        test_problem_string = f.read()
    return other_domain.domain_for_goal_prompting(test_problem_string)


def test_alfred_for_goal_prompting():
    TEST_DOMAIN_OTHER = "data/domains/alfred_linearized.pddl"
    with open(TEST_DOMAIN_OTHER) as g:
        domain = Domain(pddl_domain=g.read())
    TEST_PDDL_PROBLEM_FILE = "data/dataset/alfred-sample-problem-0-0.pddl"
    with open(TEST_PDDL_PROBLEM_FILE) as f:
        test_problem_string = f.read()
    return domain.domain_for_goal_prompting(test_problem_string)

