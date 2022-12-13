### LLM-Operators
Learning planning domain models from natural language and grounding.

### ALFRED experiment quickstart. This sets up the repository to run experiments with the ALFRED dataset.
1. *Download the ALFRED PDDL files*. We use a preprocessed set of Alfred files that is available [here](https://drive.google.com/file/d/1sg8v1hf40Eu1K7hLGZ_LP5I-9N4zwLCU/view?usp=sharing), and should be placed in `dataset/alfred_linearized_pddl`. This contains the PDDL paths referenced in `dataset/alfred-linearized-100-NLgoals-operators.json`.

To prepare this from scratch, use the dataset [here](https://drive.google.com/file/d/1sg8v1hf40Eu1K7hLGZ_LP5I-9N4zwLCU/view?usp=sharing), and is originally copied from the MIT internal version at `/data/vision/torralba/datasets/ALFRED/data/full_2.1.0/`. We extract this to `dataset/alfred_pddl`; you should see three internal folders (train, valid_seen, valid_unseen). This provides the PDDL paths referenced in `dataset/alfred-NLgoal-operators.json`.
   - Prepare the ALFRED PDDL files. We modify the ALFRED domain to support simple fast downward planning. Run `prepare_alfred_pddl.py` to do so, or, download our extracted and updated version at [TBD].


2. *Install the submodules*. You can install these with
There are two relevant submodules:
- `pddlgym_planners`. This contains a fast-downward task planner.
- `alfred`. This is a fork of the main ALFRED repository (https://github.com/jiahai-feng/alfred) that we have updated to support task and motion planning from PDDL with custom operators.

3. *Create a Python environment*. This conda environment has been tested on the following machines so far:
- 

4. *Add an OpenAI environment key.* You will need to edit your bash_profile or enviromment to include a line that contains `export OPENAI_API_KEY=<OPEN_AI_KEY>` and ask Cathy (zyzzyva@mit.edu) if you need one.

6. *Test your Thor installation.*

7. *Test your learning loop.* 
- The entrypoint to the full learning loop is currently at `main.py`.
- This demo test command loads `dataset_fraction` fraction of the dataset and begins running a single full training iteration: 
```
python main.py --dataset_name alfred_linearized_100 --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle --verbose --train_iterations 1 --dataset_pddl_directory dataset/alfred_linearized_pddl --output_directory generated/test_outputs --debug_mock_propose_plans --debug_mock_propose_operators --debug_mock_propose_goals 
```
--------------------------------------------
### ALFRED experiments. This dev section contains details on experiments run at each portion of the ALFRED loop.
##### ALFRED PDDL dataset.
1. Planning domains and datasets are housed in `datasets.py`. This registers datasets and PDDL domains loaded with the `--dataset_name` and `--pddl_domain_name` flags. 
- PDDL domains are in domains. We created a custom version of the ALFRED domain and files, since our task planner is just used to ensure faster search. This was initially done by running `prepare_alfred_pddl.py` on the dataset originally extracted from above.

This script prepares a *subset* of the original dataset, and modifies both the PDDL domain (alfred_linearized.pddl) and the problem files (in alfred_linearized/pddl).

It was also used to produced the `alfred_linearized_100` subset of the dataset.

2. Codex. We use Codex to propose goal, initial plan, and operator definitions. This is housed in `codex.py`.
- Proposing plans. This is 


--------------------------------------------
#### AWS Experiments.

##### AWS setup.
1. Launch machines at https://889121882474.signin.aws.amazon.com/console
- This only applies to MIT setup.

