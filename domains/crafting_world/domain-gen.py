#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File   : domain-gen.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 01/06/2023
#
# This file is part of HACL-PyTorch.
# Distributed under terms of the MIT license.


def load_source(filename, name=None):
    import os.path as osp
    from importlib.machinery import SourceFileLoader

    if name is None:
        basename = osp.basename(filename)
        if basename.endswith('.py'):
            basename = basename[:-3]
        name = basename.replace('.', '_')

    return SourceFileLoader(name, filename).load_module()


def underline_to_pascal(s):
    return ''.join([w.capitalize() for w in s.split('_')])


mining_template_0 = """
 (:action {action_name}
  :parameters (?targetinv - inventory ?x - object ?target - object ?t - tile)
  :precondition (and
    (agent-at ?t)
    (object-at ?x ?t)
    (object-of-type ?x {target_type})
    (inventory-empty ?targetinv)
    (object-of-type ?target Hypothetical)
  )
  :effect (and
    (not (inventory-empty ?targetinv))
    (inventory-holding ?targetinv ?target)
    (not (object-of-type ?target Hypothetical))
    (object-of-type ?target {create_type})
  )
 )"""


mining_template_1 = """
 (:action {action_name}
  :parameters (?toolinv - inventory ?targetinv - inventory ?x - object ?tool - object ?target - object ?t - tile)
  :precondition (and
    (agent-at ?t)
    (object-at ?x ?t)
    (object-of-type ?x {target_type})
    (inventory-holding ?toolinv ?tool)
    (object-of-type ?tool {holding})
    (inventory-empty ?targetinv)
    (object-of-type ?target Hypothetical)
  )
  :effect (and
    (not (inventory-empty ?targetinv))
    (inventory-holding ?targetinv ?target)
    (not (object-of-type ?target Hypothetical))
    (object-of-type ?target {create_type})
  )
 )"""

crafting_template_1 = """
 (:action {action_name}
  :parameters (?ingredientinv1 - inventory ?targetinv - inventory ?station - object ?ingredient1 - object ?target - object ?t - tile)
  :precondition (and
    (agent-at ?t)
    (object-at ?station ?t)
    (object-of-type ?station {station_type})
    (inventory-holding ?ingredientinv1 ?ingredient1)
    (object-of-type ?ingredient1 {ingredient1_type})
    (inventory-empty ?targetinv)
    (object-of-type ?target Hypothetical)
  )
  :effect (and
    (not (inventory-empty ?targetinv))
    (inventory-holding ?targetinv ?target)
    (not (object-of-type ?target Hypothetical))
    (object-of-type ?target {create_type})
    (not (inventory-holding ?ingredientinv1 ?ingredient1))
    (inventory-empty ?ingredientinv1)
    (not (object-of-type ?ingredient1 {ingredient1_type}))
    (object-of-type ?ingredient1 Hypothetical)
  )
 )"""

crafting_template_2 = """
 (:action {action_name}
  :parameters (?ingredientinv1 - inventory ?ingredientinv2 - inventory ?targetinv - inventory ?station - object ?ingredient1 - object ?ingredient2 - object ?target - object ?t - tile)
  :precondition (and
    (agent-at ?t)
    (object-at ?station ?t)
    (object-of-type ?station {station_type})
    (inventory-holding ?ingredientinv1 ?ingredient1)
    (object-of-type ?ingredient1 {ingredient1_type})
    (inventory-holding ?ingredientinv2 ?ingredient2)
    (object-of-type ?ingredient2 {ingredient2_type})
    (inventory-empty ?targetinv)
    (object-of-type ?target Hypothetical)
  )
  :effect (and
    (not (inventory-empty ?targetinv))
    (inventory-holding ?targetinv ?target)
    (not (object-of-type ?target Hypothetical))
    (object-of-type ?target {create_type})
    (not (inventory-holding ?ingredientinv1 ?ingredient1))
    (inventory-empty ?ingredientinv1)
    (not (object-of-type ?ingredient1 {ingredient1_type}))
    (object-of-type ?ingredient1 Hypothetical)
    (not (inventory-holding ?ingredientinv2 ?ingredient2))
    (inventory-empty ?ingredientinv2)
    (not (object-of-type ?ingredient2 {ingredient2_type}))
    (object-of-type ?ingredient2 Hypothetical)
  )
 )"""


def main():
    rules = load_source('./crafting_world_rules.py')

    mining_rules = ''
    for r in rules.MINING_RULES:
        action_name = r['rule_name'].replace('_', '-')
        create_type = underline_to_pascal(r['create'])
        target_type = underline_to_pascal(r['location'])
        holding = r['holding'][0] if len(r['holding']) == 1 else None
        if holding is not None:
            holding = underline_to_pascal(holding)

        if holding is None:
            mining_rules += mining_template_0.format(action_name=action_name, create_type=create_type, target_type=target_type)
        else:
            mining_rules += mining_template_1.format(action_name=action_name, create_type=create_type, target_type=target_type, holding=holding)

    crafting_rules = ''
    for r in rules.CRAFTING_RULES:
        action_name = r['rule_name'].replace('_', '-')
        create_type = underline_to_pascal(r['create'])
        station_type = underline_to_pascal(r['location'])
        recipe = list(map(underline_to_pascal, r['recipe']))

        if len(recipe) == 1:
            ingredient1_type = recipe[0]
            crafting_rules += crafting_template_1.format(action_name=action_name, create_type=create_type, station_type=station_type, ingredient1_type=ingredient1_type)
        elif len(recipe) == 2:
            ingredient1_type, ingredient2_type = recipe
            crafting_rules += crafting_template_2.format(action_name=action_name, create_type=create_type, station_type=station_type, ingredient1_type=ingredient1_type, ingredient2_type=ingredient2_type)
        else:
            raise ValueError('Invalid recipe length: {}'.format(len(recipe)))

    with open('./domain.pddl-template') as f:
        template = f.read()
    with open('./domain.pddl', 'w') as f:
        f.write(template.format(mining_rules=mining_rules, crafting_rules=crafting_rules))
    print('Generated: domain.pddl')


if __name__ == '__main__':
    main()

