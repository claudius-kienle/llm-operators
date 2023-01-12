import os
import json
import pathlib

RANDOM_SEED = 0


def get_output_directory(curr_iteration, command_args, experiment_name_to_load):
    output_directory = command_args.output_directory

    full_output_directory = os.path.join(
        output_directory, experiment_name_to_load, str(curr_iteration)
    )
    pathlib.Path(full_output_directory).mkdir(parents=True, exist_ok=True)
    return full_output_directory


def output_iteration_summary(
    curr_iteration, pddl_domain, problems, command_args, output_directory
):
    # Log the best operators for resumption.
    experiment_tag = (
        ""
        if len(command_args.experiment_name) < 1
        else f"{command_args.experiment_name}_"
    )
    output_filepath = f"{experiment_tag}all_operators.json"
    with open(output_filepath, "w") as f:
        f.write(pddl_domain.to_string(pddl_domain.to_string()))

    # Print the total experiment progress.
    print("=========EXPERIMENT SUMMARY=================")
    print(f"\titeration: {curr_iteration}")
    print(
        f"\tevaluated successful motion plans: {len([p for p in problems.values() if p.best_evaluated_plan_at_iteration is not None])}"
    )
    for p in problems.values():
        if p.best_evaluated_plan_at_iteration is not None:
            print(f"\t\tSOLVED - {p.language}")
            print(
                f"\t\t{list(p.evaluated_motion_planner_results.values())[0].pddl_plan.plan_string}"
            )
    print(f"\ttotal problems: {len(problems)}")
    print(f"\tcurrent operators: {len(problems)}")
    print("=========EXPERIMENT SUMMARY=================")

