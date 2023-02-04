#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import json

import numpy as np

from llm_operators.datasets.core import Problem, register_planning_pddl_domain, register_planning_domain_problems
from llm_operators.datasets.dataset_utils import load_pddl_file_with_operators
from llm_operators.pddl import PDDLProblem

CRAFTING_WORLD_PDDL_DOMAIN_NAME = 'crafting_world'
CRAFTING_WORLD_PDDL_DOMAIN_FILE = 'data/domains/crafting_world/domain.pddl'


@register_planning_pddl_domain(CRAFTING_WORLD_PDDL_DOMAIN_NAME)
def load_crafting_world_pddl_domain(verbose=False):
    return load_pddl_file_with_operators(
        domain_name=CRAFTING_WORLD_PDDL_DOMAIN_NAME,
        file_path=CRAFTING_WORLD_PDDL_DOMAIN_FILE,
        verbose=verbose,
    )
