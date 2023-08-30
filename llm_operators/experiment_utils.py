import os
import sys
import json
import pathlib
import datetime

# TODO(Jiayuan Mao @ 2023/02/04): use a principled way to control the random seed.
RANDOM_SEED = 0


def should_use_checkpoint(curr_iteration, curr_problem_idx, resume_from_iteration, resume_from_problem_idx):
    # Should we attempt to load from a checkpoint?
    if curr_iteration <= resume_from_iteration:
        if curr_problem_idx is None or curr_problem_idx <= resume_from_problem_idx:
            return True
    return False


def get_output_directory(curr_iteration, command_args, experiment_name_to_load):
    output_directory = command_args.output_directory

    if curr_iteration is None:
        full_output_directory = os.path.join(output_directory, experiment_name_to_load)
    else:
        full_output_directory = os.path.join(output_directory, experiment_name_to_load, str(curr_iteration))
    pathlib.Path(full_output_directory).mkdir(parents=True, exist_ok=True)
    return full_output_directory


def output_iteration_summary(
    curr_iteration, pddl_domain, problems, command_args, output_directory, finished_epoch, problem_idx, total_problems
):
    # Print the total experiment progress.
    print('Experiment Summary')
    print("=" * 80)
    print(f"iteration: {curr_iteration}")
    print(f"evaluated successful motion plans: {len([p for p in problems.values() if len(p.solved_motion_plan_results) > 0])} / {problem_idx + 1} problems so far of {total_problems} total problems in this iteration.")
    if finished_epoch:
        for p in problems.values():
            if len(p.solved_motion_plan_results) > 0:
                plan_string = list(p.solved_motion_plan_results.values())[0].pddl_plan.plan_string.replace('\n', ' ')
                print(f"  SOLVED - {p.language}")
                print(f"  {plan_string}")
    print(f"total problems: {len(problems)}")
    print(f"current operators: {len(problems)}")
    print('')


def output_experiment_parameters(command_args):
    command_args_string = ""
    for command, args in vars(command_args).items():
        if type(args) == list:
            args_str = " ".join(args)
        elif type(args) == bool:
            args_str = ""  # action=store_true
        else:
            args_str = args
        command_args_string += f"--{command} {args_str} "

    print('Experiment Parameters')
    print('=' * 80)
    print(f"Timestamp: {datetime.datetime.now()}")
    print(f"Command to replicate: python main.py {command_args_string}")
    print('')

    directory = get_output_directory(None, command_args, command_args.experiment_name)
    filename = os.path.join(directory, "command_args.json")
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump(vars(command_args), f, indent=4)
    filename = os.path.join(directory, "command_args.txt")
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(' '.join(sys.argv))
            f.write(command_args_string)
