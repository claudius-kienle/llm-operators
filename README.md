### LLM-Operators
Learning planning domain models from natural language and grounding.
See experiments_README.md for a log of development commands.

### ALFRED experiment quickstart. This sets up the repository to run experiments with the ALFRED dataset.
1. *Download the ALFRED PDDL files*. We use a preprocessed set of Alfred files that is available [here](https://drive.google.com/drive/u/0/folders/1sE90a87rWNHPzwwm3HPg_XAxyi6HTOBc), and should be placed in `data/dataset/alfred_linearized_pddl`. This contains the PDDL paths referenced in `dataset/alfred-linearized-100-NLgoals-operators.json`.

To prepare this from scratch, use the dataset [here](https://drive.google.com/file/d/1sg8v1hf40Eu1K7hLGZ_LP5I-9N4zwLCU/view?usp=sharing), and is originally copied from the MIT internal version at `/data/vision/torralba/datasets/ALFRED/data/full_2.1.0/`. We extract this to `dataset/alfred_pddl`; you should see three internal folders (train, valid_seen, valid_unseen). This provides the PDDL paths referenced in `dataset/alfred-NLgoal-operators.json`.
   - Prepare the ALFRED PDDL files. We modify the ALFRED domain to support simple fast downward planning. Run `prepare_alfred_pddl.py` to do so, or, download our extracted and updated version at [TBD].


2. *Install the submodules*. You can install these with
There are two relevant submodules:
- `pddlgym_planners`. This contains the fast-downward task planner that we use in llm_operators/task_planner.py
- `alfred`. This is a fork of the main ALFRED repository (https://github.com/jiahai-feng/alfred) that we have updated to support task and motion planning from PDDL with custom operators.

3. *Add an OpenAI environment key.* You will need to edit your bash_profile or enviromment to include a line that contains `export OPENAI_API_KEY=<OPEN_AI_KEY>` and ask Cathy (zyzzyva@mit.edu) if you need one.


4. *Create a Python environment*. This conda environment has been tested on the following machines so far:
- 

5. *Test your Thor installation.* You shoudl be able to run the alfred/test_thor.py function to check your installation.

7. *Test your learning loop.* 
- The entrypoint to the full learning loop is currently at `main.py`.
- This demo test command loads `dataset_fraction` fraction of the dataset and begins running a single full training iteration: 
```
python main.py --experiment_name alfred_linearized_100_supervision_pddl_pick_place_clean --dataset_name alfred_linearized_100 --supervision_name supervision --pddl_domain_name alfred_linearized --dataset_fraction 1.0 --training_plans_fraction 1.0 --initial_plans_prefix pick_and_place_simple pick_clean_then_place_in_recep --initial_pddl_operators GotoLocation PickupObjectInReceptacle PickupObjectNotInReceptacle PutObjectInReceptacle PutReceptacleObjectInReceptacle CleanObject --verbose --train_iterations 1 --dataset_pddl_directory data/dataset/alfred_linearized_pddl --output_directory generated`
```
--------------------------------------------
##### Adding in new domains. 
The following describes how we add in the ALFRED domain, which comprises a ground truth PDDL domain file, a set of individual PDDL tasks and NL annotations, and a motion planner.
1. Registering a PDDL domain: to register a new PDDL domain (which you can then specify using the `--pddl_domain_name` flag for `main.py`), you should register a new PDDL domain file loader, like the ALFRED example [here](https://github.com/CatherineWong/llm-operators/blob/main/datasets.py#L201), which initializes a new [Domain](https://github.com/CatherineWong/llm-operators/blob/main/pddl.py#L14) object. Our example also optionally implements a `operator_canonicalization` and `codex_types` attribute that is only used to construct Codex prompts, and is probably not necessary for new, non-ALFRED domains. In general, this PDDL file should contain both a set of ground truth operators and all of the predicates you want to plan over in FD and prompt Codex with.
2. Registering a dataset of new tasks: register a new dataset loader (which you can then specify using the `--dataset_name` flag for `main.py`) , like the example [here](https://github.com/CatherineWong/llm-operators/blob/main/datasets.py#L447). This should load both a set of PDDL problem files (the ALFRED ones are downloaded separately, see below, ALFRED PDDL dataset) and NL annotations, and creates a {<SPLIT_NAME> : {task_id : [Problem](https://github.com/CatherineWong/llm-operators/blob/main/datasets.py#L14)}} structure for loading train/test splits of problems.
These two steps should be enough to get the basic task planning + Codex portion running. To then add a domain-specific motion planner,
3. Adding a motion planner: you'd add in another motion planner [here](https://github.com/CatherineWong/llm-operators/blob/main/motion_planner.py#L30).

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

