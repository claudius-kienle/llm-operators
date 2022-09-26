"""
test_planning_domain.py | Classes for representing planning domains and planning domain datasets.
"""
from planning_domain import *


def test_load_alfred_planning_problems():
    planning_domain_loader = PLANNING_PROBLEMS_REGISTRY[ALFRED_DATASET_NAME]

    domain = planning_domain_loader(verbose=True)


def test_load_alfred_pddl_domain():
    domain_loader = PLANNING_PDDL_DOMAINS_REGISTRY[ALFRED_PDDL_DOMAIN_NAME]
    domain = domain_loader(verbose=True)


def main():
    test_load_alfred_planning_problems()
    test_load_alfred_pddl_domain()


if __name__ == "__main__":
    main()
