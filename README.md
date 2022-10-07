### LLM-Operators
Learning planning domain models from natural language and grounding.

### ALFRED Domain.
- The ALFRED dataset file in `dataset/alfred-NLgoal-operators.json` makes reference to external PDDL files that come from the full, original ALFRED PDDL dataset.
- A full MIT internal version of this dataset is located at `/data/vision/torralba/datasets/ALFRED/data/full_2.1.0/`
- A PDDL-only version of this dataset can be extracted from [here](https://drive.google.com/file/d/1B4zi0htKbHIBzghPmSKio_7ZEGoZLaKG/view?usp=sharing).

### Installation and setup.
The installation and setup is in progress, so is described here according to the modular portions.

- The entrypoint to the full learning loop is currently at `main.py`.
- This demo test command loads `dataset_fraction` fraction of the dataset and begins running a single full training iteration: 
```
python main.py 
--dataset_name alfred  # Dataset of planning problems.
--pddl_domain_name alfred # Ground truth PDDL domain.
--dataset_fraction 0.001 # Fraction of full dataset.
--training_plans_fraction 0.1 # Fraction of given dataset to supervise on.
--initial_pddl_operators GotoLocation OpenObject  # Initialize with these operators.
--verbose # Include for verbose.
--train_iterations 1 # How many operations.
--dataset_pddl_directory dataset/alfred_pddl # Location of the PDDL ground truth files, if applicable.
```

#### Task-level domain definition proposal (LLM)
- In this step, we attempt to propose task-level (PDDL) domain definitions of goals, operators and predicates, given natural language goals and a few initial example PDDL operators and predicates.
- This has been tested locally on an M1 Mac using a Conda environment initialized using the `environment.yaml`.
- This requires an OpenAI environment key. Edit your bash_profile to include a line like `export OPENAI_API_KEY=<OPEN_AI_KEY>` and ask Cathy (zyzzyva@mit.edu) if you need one.
- Key functions are defined in `codex.py`.

#### Task-level planning (PDDL solver)
- In this step, we attempt to verify proposed goals, predicates, and operators at the task level.
- This is being implemented in `task_planner.py`

