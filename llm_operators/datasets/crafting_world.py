#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path as osp
import itertools
import json

from llm_operators.datasets.core import register_planning_pddl_domain, register_planning_domain_problems
from llm_operators.datasets.dataset_utils import load_pddl_file_with_operators
from llm_operators.datasets.crafting_world_gen.cw_20230204_minining_only import problem_from_raw_record, gen_v20230204_solution

CRAFTING_WORLD_PDDL_DOMAIN_NAME = 'crafting_world'
CRAFTING_WORLD_PDDL_DOMAIN_FILE = 'data/domains/crafting_world/domain.pddl'


@register_planning_pddl_domain(CRAFTING_WORLD_PDDL_DOMAIN_NAME)
def load_crafting_world_pddl_domain(verbose=False):
    domain = load_pddl_file_with_operators(
        domain_name=CRAFTING_WORLD_PDDL_DOMAIN_NAME,
        file_path=CRAFTING_WORLD_PDDL_DOMAIN_FILE,
        verbose=verbose,
    )
    domain.codex_types = CRAFTING_WORLD_CODEX_TYPES
    return domain


CRAFTING_WORLD_20230204_DATASET_NAME = 'crafting_world_20230204_minining_only'

@register_planning_domain_problems(CRAFTING_WORLD_20230204_DATASET_NAME)
def load_crafting_world_20230204_minining_only(dataset_pddl_directory: str, dataset_fraction: float, verbose=False):
    """Experiments crafting_world_v20230204_mining_only

        1. The map is a linear chain: t1 t2 t3 ...
        2. Agent only needs to accomplish mining tasks in this environment.
        3. All types of resources (e.g., Tree, IronOre) will be randomly distributed on the map.
        4. All types of tools (only tools that can be used for mining) will be randomly distributed on the map.
        5. The agent starts at tile 1.
        6. To solve the task, the "GT" plan is to find a corresponding tool, pick it up, navigate to the resource tile, and execute mining.
        7. Instructions are generated with a single template: Mine X from the map.

    .. code::
        python main.py --experiment_name cw_v20230204_mining_only_full --dataset_name crafting_world_20230204_minining_only --supervision_name supervision --pddl_domain_name crafting_world --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix mining --initial_pddl_operators move-up move-down move-left move-right pick-up place-down mine-iron-ore --verbose --train_iterations 1 --dataset_pddl_directory data/dataset/crafting_world_v202302024_mining_only --goal_propose_include_codex_types --operator_propose_minimum_usage 1 --output_directory generated --debug_stop_after_first_proposal

    Note that since the task planner will timeout on this domain, we need to implement a new task planner (skipped for now, only testing for proposals).
    See generated/cw_v20230204_mining_only_full/0/cw_v20230204_mining_only_full_preprocessed_operators.csv for results.
    """
    with open(osp.join(dataset_pddl_directory, 'dataset.json')) as f:
        dataset = json.load(f)

    for split, split_problems in dataset.items():
        dataset[split] = {
            problem['problem_id']: problem_from_raw_record(problem)
            for problem in split_problems[:int(len(split_problems) * dataset_fraction)]
        }

    assert len(dataset['train']) > 3
    for problem in itertools.islice(dataset['train'].values(), 3):
        problem.should_supervise_pddl = True

    return dataset


CRAFTING_WORLD_CODEX_TYPES = """
 (:constants
  Key - object-type
  WorkStation - object-type
  Pickaxe - object-type
  IronOreVein - object-type
  IronOre - object-type
  IronIngot - object-type
  CoalOreVein - object-type
  Coal - object-type
  GoldOreVein - object-type
  GoldOre - object-type
  GoldIngot - object-type
  CobblestoneStash - object-type
  Cobblestone - object-type
  Axe - object-type
  Tree - object-type
  Wood - object-type
  WoodPlank - object-type
  Stick - object-type
  WeaponStation - object-type
  Sword - object-type
  Chicken - object-type
  Feather - object-type
  Arrow - object-type
  ToolStation - object-type
  Shears - object-type
  Sheep - object-type
  Wool - object-type
  Bed - object-type
  BedStation - object-type
  BoatStation - object-type
  Boat - object-type
  SugarCanePlant - object-type
  SugarCane - object-type
  Paper - object-type
  Furnace - object-type
  FoodStation - object-type
  Bowl - object-type
  PotatoPlant - object-type
  Potato - object-type
  CookedPotato - object-type
  BeetrootCrop - object-type
  Beetroot - object-type
  BeetrootSoup - object-type

  Hypothetical - object-type
  Trash - object-type
 )
"""
