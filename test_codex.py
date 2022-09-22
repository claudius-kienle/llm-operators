"""
test_codex.py | Tests for codex.py.
"""
from codex import propose_operator_definition
from pddl_parser import *


def create_mock_domain(domain_file="domains/alfred.pddl"):
    # Create a structured test object from a planning domain.
    # Loads a PDDL domain.
    with open(os.path.join(domain_file)) as f:
        raw_pddl = f.read()
    domain = Domain(pddl_domain=raw_pddl)
    return domain


def create_mock_ablated_domain(
    domain, operators_to_keep=["GotoLocation", "OpenObject"]
):
    # Create a mock domain with only a few operators.
    for o in list(domain.operators.keys()):
        if o not in operators_to_keep:
            domain.remove_operator(o)
    return domain


def create_mock_operator_uses():
    # Create a few sample operator uses for the ALFRED domain.
    return {
        "GotoLocation": [
            "(GotoLocation agent1 loc_1 loc_2)",
            "(GotoLocation agent1 loc_2 loc_3)",
            "(GotoLocation agent1 loc_2 loc_5)",
        ],
        "OpenObject": [
            "(OpenObject agent1 loc_1 Microwave)",
            "(OpenObject agent1 Fridge)",
            "(OpenObject agent1 GarbageCan)",
        ],
        "CloseObject": [
            "(CloseObject agent1 loc_1 Microwave)",
            "(CloseObject agent1 loc_2 Fridge)",
            "(CloseObject agent1 loc_3 Fridge)",
        ],
    }


def test_propose_operator_definition():
    mock_ground_truth_domain = create_mock_domain()
    ablated_domain = create_mock_ablated_domain(
        domain=create_mock_domain(), operators_to_keep=["GotoLocation", "OpenObject"]
    )
    mock_uses = create_mock_operator_uses()

    operator_name_to_define = "CloseObject"
    operator_definitions = propose_operator_definition(
        current_domain=ablated_domain,
        operator_name_to_define=operator_name_to_define,
        operator_uses=mock_uses,
        verbose=True,
    )
    assert len(operator_definitions) == 1
    # Compare it to the ground truth.
    print("Ground truth: ")
    print(mock_ground_truth_domain.operators[operator_name_to_define])
    print("Proposed: ")
    print(operator_definitions[0])


def test_propose_operator_uses():
    # TODO: NK
    pass


def main():
    # Test the proposed operator definitions -- CW.
    test_propose_operator_definition()


if __name__ == "__main__":
    main()
