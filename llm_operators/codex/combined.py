from llm_operators.codex.codex_core import get_solved_unsolved_problems
from llm_operators.codex.operator import DEFAULT_OPERATOR_TEMPERATURE, propose_operators_for_problems, use_ground_truth_operators
from llm_operators.codex.plan import propose_plans_for_problems


def propose_plans_operators_for_problems(
    current_domain,
    problems,
    supervision_pddl=[],
    n_plan_samples=5,
    n_operator_samples=5,
    minimum_usage=2,  # Minimum time the operator was used.
    plan_temperature=1.0,
    operator_temperature=DEFAULT_OPERATOR_TEMPERATURE,
    verbose=False,
    output_directory=None,
    command_args=None,
    use_gt=False,
    external_plan_supervision=None,
    external_operator_supervision=None,
    external_operator_sample_with_prompt=True,
    external_operator_names=None,
    operator_use_cot=True,
    resume=False,
    resume_from_iteration=None,
    resume_from_problem_idx=None,
    curr_iteration=None,
    debug_skip_propose_operators_after=None,
    debug_skip_propose_plans_after=None,
):
    unsolved_problems, solved_problems = get_solved_unsolved_problems(problems, context='pddl_plan')
    if use_gt:
        use_ground_truth_operators(current_domain, verbose)
        return

    # Condition on: NL goals. Propose: PDDL plans.
    propose_plans_for_problems(
        unsolved_problems=unsolved_problems,
        solved_problems=solved_problems,
        current_domain=current_domain,
        supervision_pddl=supervision_pddl,
        n_samples=n_plan_samples,
        temperature=plan_temperature,
        verbose=verbose,
        output_directory=output_directory,
        experiment_name=command_args.experiment_name,
        use_mock=command_args.debug_mock_propose_plans,
        external_plan_supervision=external_plan_supervision,
        resume=resume,
        resume_from_iteration=resume_from_iteration,
        resume_from_problem_idx=resume_from_problem_idx,
        curr_iteration=curr_iteration,
        debug_skip_propose_plans_after=debug_skip_propose_plans_after,
    )
    # Condition on: new operator names. Propose: PDDL operator definitions.
    propose_operators_for_problems(
        problems=problems,
        current_domain=current_domain,
        supervision_pddl=supervision_pddl,
        verbose=verbose,
        minimum_usage=minimum_usage,
        temperature=operator_temperature,
        n_samples=n_operator_samples,
        output_directory=output_directory,
        initial_pddl_predicates=command_args.initial_pddl_predicates,
        experiment_name=command_args.experiment_name,
        use_mock=command_args.debug_mock_propose_operators,
        external_operator_supervision=external_operator_supervision,
        external_operator_sample_with_prompt=external_operator_sample_with_prompt,
        external_operator_names=external_operator_names,
        use_cot=operator_use_cot,
        resume=resume,
        resume_from_iteration=resume_from_iteration,
        resume_from_problem_idx=resume_from_problem_idx,
        curr_iteration=curr_iteration,
        debug_skip_propose_operators_after=debug_skip_propose_operators_after,
    )
