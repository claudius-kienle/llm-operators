#### Experiments log.

#### Supervision PDDL, alfred_linearized_100 pick and place.
Original command: ```python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated/test_outputs```

Replicate with mock data using:
 ```python main.py --experiment_name alfred_linearized_100 --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated/test_outputs --debug_mock_propose_plans```

_Codex proposal notes:_
Supervision on external PDDL plans. Initialized only with pick and place.
We now construct a prompt containing handwritten natural language and PDDL plans/operators from external IPC problems. See:
    - `dataset/supervision-NL.json`
    - `supervision-NLgoals-operators.json`. 

- Plan proposal notes: `generated/test_outputs/alfred_linearized_100_supervision_pddl_pick_place_codex_plans.json`: much more diverse but redundant plan set.

Supervision using the 'linearized' pick and place operators in `alfred_linearized.pddl`. 
- Operator proposal notes: 

_Task planning notes:_