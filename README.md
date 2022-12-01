### LLM-Operators
Learning planning domain models from natural language and grounding.

### ALFRED Domain.
- The ALFRED dataset file in `dataset/alfred-NLgoal-operators.json` makes reference to external PDDL files that come from the full, original ALFRED PDDL dataset.
- A full MIT internal version of this dataset is located at `/data/vision/torralba/datasets/ALFRED/data/full_2.1.0/`
- A PDDL-only version of this dataset can be extracted from [here](https://drive.google.com/file/d/1sg8v1hf40Eu1K7hLGZ_LP5I-9N4zwLCU/view?usp=sharing).

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
- This requires you to have installed openai
- In this step, we attempt to propose task-level (PDDL) domain definitions of goals, operators and predicates, given natural language goals and a few initial example PDDL operators and predicates.
- This has been tested locally on an M1 Mac using a Conda environment initialized using the `environment.yaml`.
- This requires an OpenAI environment key. Edit your bash_profile to include a line like `export OPENAI_API_KEY=<OPEN_AI_KEY>` and ask Cathy (zyzzyva@mit.edu) if you need one.
- Key functions are defined in `codex.py`.
- You can test this with: 

#### Task-level planning (PDDL solver)
- Download the pddlgym_planners github repo into this one. This will be ignored. Running the installation should create the desired planner.

--------------------------------------------
#### AWS Experiments.

##### AWS setup.
1. Launch machines at https://889121882474.signin.aws.amazon.com/console
- This only applies to MIT setup.

To create a machine for the first time:
- Login to the AWS console at ` `  
- We created the following base machine: AMI Image `Ubuntu Pro 18.04 LTS`, Instance Type: g2.2xlarge, 100 GiB gp2 storage.
- Generate an SSH key and add to your github: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Attempt to install Python 3.7
```
sudo apt-get update; sudo apt-get install software-properties-common; 
sudo add-apt-repository ppa:deadsnakes/ppa; sudo apt-get update; 
sudo apt-get install python3.7; sudo apt install python3.7-dev; 
sudo apt install python3-pip; python3.7 -m pip install pip;
pip3 install --upgrade setuptools; sudo apt install virtualenv
```
Attempt to install ALFRED:
- Git clone: https://github.com/jiahai-feng/alfred
```
export ALFRED_ROOT=$(pwd)/alfred
virtualenv -p $(which python3.7) --system-site-packages alfred_env
pip3 install -r requirements.txt
```
- Install NVDIA drivers:
```

sudo ubuntu-drivers autoinstall
```
Reboot.


- Start a display, following the ALFREd instructions under "Run (Headless)"
```
# inside docker
  tmux new -s startx  # start a new tmux session

  # start nvidia-xconfig
  sudo nvidia-xconfig -a --use-display-device=None --virtual=1280x1024

  # start X server on DISPLAY 0
  # single X server should be sufficient for multiple instances of THOR
  sudo python ~/alfred/scripts/startx.py 0  # if this throws errors e.g "(EE) Server terminated with error (1)" or "(EE) already running ..." try a display > 0

  # detach from tmux shell
  # Ctrl+b then d

  # source env
  source ~/alfred_env/bin/activate
  
  # set DISPLAY variable to match X server
  export DISPLAY=:0

  # check THOR
  cd $ALFRED_ROOT
  python scripts/check_thor.py
```
- See errors at: https://medium.com/@etendue2013/how-to-run-ai2-thor-simulation-fast-with-google-cloud-platform-gcp-c9fcde213a4a
