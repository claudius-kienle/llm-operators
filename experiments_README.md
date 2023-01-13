#### Experiments log.
### Supervision PDDL, alfred_linearized_100 pick and place.
This top-level command (without any of the checkpointing flags) will run the model on the ```alfred_linearized_100`` dataset of goals, with the GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle operators (pick and place).

```python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated```

================================================================
### Supervision PDDL, alfred_linearized_100 pick and place. How many of the Codex-proposed goals could we solve if we used the ground truth operator set? 
```--experiment_name  alfred_linearized_100_codex_goals_gt_operators```

To run:
```python main.py --experiment_name alfred_linearized_100_codex_goals_gt_operators --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated --debug_ground_truth_operators --debug_skip_motion_plans```
To debug once its run with the cached goals:
````python main.py --experiment_name alfred_linearized_100_codex_goals_gt_operators --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated --debug_ground_truth_operators --debug_skip_motion_plans --debug_mock_propose_goals```




================================================================
#### First end-end run. Supervision PDDL, alfred_linearized_100 pick and place. (Experiment tag: alfred_linearized_100_supervision_pddl_pick_place_1_13_2023)
# alfred_linearized_100_supervision_pddl_pick_place_1_13_2023 - contains the first end-end run from commit: https://github.com/CatherineWong/llm-operators/commit/f2d82771edaad76e3d4559b797fe9d692250ff88 
# Resuming this means you need to resume with 
```--experiment_name  alfred_linearized_100_supervision_pddl_pick_place_1_13_2023 experiment_name```
Original command: ```python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated```

Replicate with cached operators and GT goals using:
 ```python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated/test_outputs --debug_mock_propose_plans --debug_mock_propose_operators --debug_ground_truth_goals```

Replicate with plan proposal and operators, but with goal proposal:
```python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated --debug_mock_propose_plans --debug_mock_propose_operators```

Replicate with cached operators and goals:
```python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated --debug_mock_propose_plans --debug_mock_propose_operators --debug_mock_propose_goals```


_Codex proposal notes:_
Supervision on external PDDL plans. Initialized only with pick and place.
We now construct a prompt containing handwritten natural language and PDDL plans/operators from external IPC problems. See:
    - `dataset/supervision-NL.json`
    - `supervision-NLgoals-operators.json`. 

- Plan proposal notes: `generated/alfred_linearized_100_supervision_pddl_pick_place_codex_plans.json`: much more diverse but redundant plan set.

Supervision using the 'linearized' pick and place operators in `alfred_linearized.pddl`. Also don't use pick/place, only use GoToLocation. No external PDDL.
- Operator proposal notes: `alfred_linearized_100_supervision_pddl_pick_place_codex_operators.json`

_Task planning notes:_
Planning with the ground truth *linearized* goals.
Replicate with mock data, GT goals, and task plans using:
(NB: only the task plans files are mocked out. There isn't currently a good way to load this.)
 ```python main.py --experiment_name alfred_linearized_100_supervision_ground_truth_goals_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated --debug_mock_propose_plans --debug_mock_propose_operators --debug_ground_truth_goals --debug_mock_task_plans```

Planning with the Codex-proposed linearized goals.
 ```python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated --debug_mock_propose_plans --debug_mock_propose_operators --debug_ground_truth_goals --debug_mock_task_plans```

_Motion planning notes:_
To skip motion planning (and assume that all task plans succeeded):
 ```python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated --debug_mock_propose_plans --debug_mock_propose_operators --debug_mock_propose_goals --debug_mock_task_plans --debug_skip_motion_plans```

 Otherwise, you will need to run the commmand without `--debug_skip_motion_plans` to run the motion planner.

To run with motion plans, you can run: 