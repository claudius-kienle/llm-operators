"""
test_planning_domain.py | Classes for representing planning domains and planning domain datasets.
"""
from planning_domain import *


def test_load_alfred_planning_domain():
    planning_domain_loader = PLANNING_PROBLEMS_REGISTRY[ALFRED_DATASET_NAME]

    domain = planning_domain_loader(verbose=True)


def main():
    test_load_alfred_planning_domain()


if __name__ == "__main__":
    main()
