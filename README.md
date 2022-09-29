### LLM-Operators
Learning planning domain models from natural language and grounding.


### Installation and setup.
- Entrypoint is at main.py
- Demo usage to load a fraction of the ALFRED dataset:
`python main.py --dataset_name alfred --pddl_domain_name alfred --dataset_fraction 0.001 --training_plans_fraction 0.1 --initial_pddl_operators GotoLocation OpenObject  --verbose`

- An early reference prototype model is at prototype_main.py
