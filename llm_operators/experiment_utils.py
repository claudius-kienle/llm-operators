import os
import json
import pathlib
import datetime

# TODO(Jiayuan Mao @ 2023/02/04): use a principled way to control the random seed.
RANDOM_SEED = 0


def get_output_directory(curr_iteration, command_args, experiment_name_to_load):
    output_directory = command_args.output_directory

    full_output_directory = os.path.join(output_directory, experiment_name_to_load, str(curr_iteration))
    pathlib.Path(full_output_directory).mkdir(parents=True, exist_ok=True)
    return full_output_directory


def output_iteration_summary(
    curr_iteration, pddl_domain, problems, command_args, output_directory, finished_epoch, problem_idx, total_problems
):
    # Print the total experiment progress.
    print("=========EXPERIMENT SUMMARY=================")
    print(f"\titeration: {curr_iteration}")
    print(
        f"\tevaluated successful motion plans: {len([p for p in problems.values() if len(p.solved_motion_plan_results) > 0])} / {problem_idx + 1} problems so far of {total_problems} total problems in this iteration."
    )
    if finished_epoch:
        for p in problems.values():
            if len(p.solved_motion_plan_results) > 0:
                print(f"\t\tSOLVED - {p.language}")
                print(f"\t\t{list(p.solved_motion_plan_results.values())[0].pddl_plan.plan_string}")
    print(f"\ttotal problems: {len(problems)}")
    print(f"\tcurrent operators: {len(problems)}")
    print("=========EXPERIMENT SUMMARY=================")


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

    print("=========EXPERIMENT PARAMETERS=================")
    print(f"Timestamp: {datetime.datetime.now()}")
    print(f"Command to replicate: python main.py {command_args_string}")
    print("=========EXPERIMENT PARAMETERS=================")
