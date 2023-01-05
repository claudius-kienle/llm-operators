"""
codex.py 
Utilities that call a large language-code model.
"""
import time
from collections import Counter, defaultdict

import datasets
import task_planner
import openai
from openai.error import APIConnectionError, InvalidRequestError, RateLimitError
import os
from time import sleep
import random
from pddl import *
from collections import defaultdict

random.seed(0)

NONE = "NONE"
STOP_TOKEN = "\n<END>\n"
OPERATOR_START = ";; Operator: "
EXAMPLE_START = ";; Example: "
NATURAL_LANGUAGE_GOAL_START = ";; Goal: "
PDDL_GOAL_START = ";; PDDL Goal: "
PDDL_PLAN_START = ";; PDDL Plan: "
OPERATOR_START_TOKEN = "(:action "
CODEX_PROMPT = "codex_prompt"
CODEX_OUTPUT = "codex_output"
NLgoals_PDDLplans_prompt = "\n;; Natural language goals and PDDL plans\n\n"


if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY is not set. Please set this in the shell via `export OPENAI_API_KEY=...`"
    )
openai.api_key = os.environ["OPENAI_API_KEY"]


def propose_plans_operators_goals_for_problems(
    current_domain,
    problems,
    supervision_pddl=[],
    n_samples=1,  # How many samples to take from codex.
    temperature=0.0,
    verbose=False,
    output_directory=None,
    command_args=None,
):
    """
    Proposes PDDL operators, goals, and plans for unsolved problems using Codex.
    Problems are updated with proposed plans and goals.
    ret: 
        proposed_codex_operators: PDDL operators proposed by Codex. 
    """
    unsolved_problems = [
        problems[p]
        for p in problems
        if (len(problems[p].evaluated_pddl_plans) == 0)
        and not problems[p].should_supervise_pddl
    ]
    solved_problems = [
        problems[p]
        for p in problems
        if (len(problems[p].evaluated_pddl_plans) > 0)
        or problems[p].should_supervise_pddl
    ]
    if verbose:
        print("Now in: propose_plans_operators_goals_for_problems: ")
        print(
            f"\t{len(unsolved_problems)} unsolved problems / {len(solved_problems)} solved problems"
        )

    # Condition on: NL goals. Propose: PDDL plans.
    propose_plans_for_problems(
        unsolved_problems=unsolved_problems,
        solved_problems=solved_problems,
        current_domain=current_domain,
        supervision_pddl=supervision_pddl,
        n_samples=n_samples,
        temperature=temperature,
        verbose=verbose,
        output_directory=output_directory,
        experiment_name=command_args.experiment_name,
        use_mock=command_args.debug_mock_propose_plans,
    )
    # Condition on: new operator names. Propose: PDDL operator definitions.
    propose_operators_for_problems(
        problems=problems,
        current_domain=current_domain,
        supervision_pddl=supervision_pddl,
        verbose=verbose,
        temperature=temperature,
        n_samples=n_samples,
        output_directory=output_directory,
        initial_pddl_predicates=command_args.initial_pddl_predicates,
        experiment_name=command_args.experiment_name,
        use_mock=command_args.debug_mock_propose_operators,
    )

    # Condition on: NL goals. Propose: PDDL goals.
    propose_goals_for_problems(
        unsolved_problems=unsolved_problems,
        solved_problems=solved_problems,
        current_domain=current_domain,
        output_directory=output_directory,
        supervision_pddl=supervision_pddl,
        verbose=verbose,
        temperature=temperature,
        initial_pddl_predicates=command_args.initial_pddl_predicates,
        experiment_name=command_args.experiment_name,
        use_mock=command_args.debug_mock_propose_goals,
        use_gt=command_args.debug_ground_truth_goals,
    )


def get_completions(
    prompt: str,
    n_samples: int = 1,
    temperature: float = 0.1,
    max_tokens: int = 256,  # Max tokens for completion only.
    engine: str = "code-davinci-002",
    stop: str = STOP_TOKEN,
    top_p=1,
    logprobs=None,
    max_attempts_rate_limit=5,
    rate_limit_seconds=30,
):
    pause_for_rate_limit = False
    completion = None
    for idx in range(max_attempts_rate_limit):
        if pause_for_rate_limit:
            print(
                f"ERR: Codex rate limit. On attempt {idx}/{max_attempts_rate_limit} after waiting {rate_limit_seconds}s."
            )
            time.sleep(rate_limit_seconds)
            rate_limit_seconds *= 2  # Exponential backoff
        try:
            completion = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temperature if top_p is None else 1.0,
                top_p=top_p if temperature is None else 1.0,
                n=n_samples,
                stop=stop,
                frequency_penalty=0,
                presence_penalty=0,
                max_tokens=max_tokens,
                logprobs=logprobs,
            )
            return [c["text"] for c in completion["choices"]]
        except InvalidRequestError as e:
            print(e)
            return e
        except RateLimitError as e:
            print(e)
            pause_for_rate_limit = True
            completion = e
        except APIConnectionError as e:
            print(e)
            pause_for_rate_limit = True
            completion = e


def propose_predicates_for_problems(problems, current_domain, use_mock):
    # TBD: to be implemented.
    pass


def propose_operators_for_problems(
    problems,
    current_domain,
    supervision_pddl,
    verbose,
    temperature,
    n_samples,
    output_directory,
    initial_pddl_predicates,
    experiment_name,
    use_mock,
    minimum_usage=2,  # Minimum time the operator was used.
):
    output_json = {}
    experiment_tag = "" if len(experiment_name) < 1 else f"{experiment_name}_"

    output_filepath = (
        f"{experiment_tag}codex_operators{'_'.join(initial_pddl_predicates)}.json"
    )

    # What operators were proposed across the problems? Rank by usage.
    operator_uses, operator_use_counts = get_operator_uses(problems)
    # Propose definitions for any operators we haven't implemented.
    proposed_operators = get_operators_to_propose(
        current_domain, operator_uses, operator_use_counts, minimum_usage
    )
    if verbose:
        print(
            f"propose_operators_for_problems: proposing for {len(proposed_operators)} operators."
        )

    # Get valid operators, and use a standardized operator mapping.
    if use_mock:
        mock_propose_operators_for_problems(
            output_filepath, proposed_operators, output_directory, current_domain
        )
        return
    for o in proposed_operators:
        codex_prompt, proposed_operator_definitions = propose_operator_definition(
            current_domain,
            o,
            operator_uses=operator_uses,
            max_operator_examples=10,
            max_usage_examples=10,
            temperature=temperature,
            n_samples=n_samples,
            verbose=verbose,
            initial_pddl_predicates=initial_pddl_predicates,
            supervision_pddl=supervision_pddl,
        )
        current_domain.proposed_operators[o] += proposed_operator_definitions
        output_json[o] = {
            CODEX_PROMPT: codex_prompt,
            CODEX_OUTPUT: proposed_operator_definitions,
        }

    if verbose:
        num_proposed = [
            o
            for o in current_domain.proposed_operators[o]
            if len(current_domain.proposed_operators[o]) > 1
        ]
        print(
            f"\npropose_operators_for_problems: proposed operators for {len(num_proposed)} / {len(proposed_operators)}"
        )
    if output_directory:
        with open(os.path.join(output_directory, output_filepath), "w") as f:
            json.dump(output_json, f)


def mock_propose_operators_for_problems(
    output_filepath, proposed_operators, output_directory, current_domain
):
    with open(os.path.join(output_directory, output_filepath), "r") as f:
        output_json = json.load(f)
    print(
        f"Now in: mock_propose_operators_for_problems: from {os.path.join(output_directory, output_filepath)}"
    )
    for o in proposed_operators:
        if o in output_json:
            current_domain.proposed_operators[o] = output_json[o][CODEX_OUTPUT]
    print(
        f"\tLoaded {len(current_domain.proposed_operators)} mock operators: \n\t"
        + "\n\t".join(current_domain.proposed_operators.keys())
    )


def get_operators_to_propose(
    current_domain, operator_uses, operator_use_counts, minimum_usage
):
    existing_operators = set(
        [
            o
            if o not in current_domain.operator_canonicalization
            else current_domain.operator_canonicalization[o]
            for o in current_domain.operators
        ]
    )
    proposed_operators = [p for p in operator_uses if p not in existing_operators]
    # Filter by those with minimum usage.
    proposed_operators = [
        p for p in proposed_operators if operator_use_counts[p] >= minimum_usage
    ]
    return proposed_operators


def get_operator_uses(problems):
    operator_use_counts = Counter()
    existing_operator_uses = defaultdict(list)
    for problem in problems.values():
        plans = []
        if problem.should_supervise_pddl:
            plans.append(problem.ground_truth_pddl_plan)
        if len(problem.evaluated_pddl_plans) > 0:
            plans.append(problem.get_best_evaluated_pddl_plan())
        if len(problem.proposed_pddl_plans) > 0:
            plans += problem.proposed_pddl_plans
        for plan in plans:
            for action_usage in plan.plan:
                existing_operator_uses[action_usage[PDDLPlan.PDDL_ACTION]].append(
                    action_usage
                )
                operator_use_counts[action_usage[PDDLPlan.PDDL_ACTION]] += 1
    return existing_operator_uses, operator_use_counts


def get_operator_from_action(action):
    """
    action:
        string of the form (action param1 param2 ..)
    returns:
        the action string (aka operator name)
    """
    tokens = action.strip("()").split(" ")
    op = tokens[0]
    return op


def propose_operator_definition(
    current_domain,
    operator_name_to_define,
    operator_uses={},
    supervision_pddl="",
    max_operator_examples=10,
    max_usage_examples=10,
    temperature=0.3,
    n_samples=3,
    verbose=False,
    initial_pddl_predicates=[],
):
    """
    Proposes an operator definition for a given domain, and optionally with examples of operator usages.
    current_domain: an existing PDDL domain.
    operator_uses: dict {operator_name: list of string uses of a given operator in PDDL plans.}
    operator_name_to_define: string name of operator to define.

    :ret: list of up to n_samples operator definitions. Empty list if prompting fails.
    """
    if verbose:
        print(
            f"propose_operator_definition: operator_name_to_define - {operator_name_to_define}"
        )
    # Codex prompt header.
    nl_header = ";;;; Define PDDL planning operators.\n\n"
    codex_prompt = nl_header
    if len(initial_pddl_predicates) <= 0:
        pddl_domain = (
            ";;;; Predicates in the PDDL domain definition.\n"
            + current_domain.domain_definition_to_string(codex_prompt=True)
            + "\n\n"
        )
        translation_header = (
            ";;;; Only use predicates and functions available in the PDDL domain.\n\n"
        )

        codex_prompt += pddl_domain + translation_header

    # Codex prompt exampler operators.
    operator_examples = random.sample(
        list(current_domain.operators.keys()),
        min(len(current_domain.operators), max_operator_examples),
    )
    for o in operator_examples:
        if o in operator_uses:
            codex_prompt += f"{OPERATOR_START}{o}\n"

            usage_examples = random.sample(
                list(operator_uses[o]), min(len(operator_uses[o]), max_usage_examples),
            )
            for use_example in usage_examples:
                codex_prompt += f"{EXAMPLE_START}{use_example}\n"
            codex_prompt += f"{current_domain.operators[o]}\n"
            codex_prompt += f"{STOP_TOKEN}\n"

    # Codex prompt for operator definition.
    codex_prompt += f"{OPERATOR_START}{operator_name_to_define}\n"
    if operator_name_to_define in operator_uses:
        for use_example in operator_uses[operator_name_to_define]:
            codex_prompt += f"{EXAMPLE_START}{use_example}\n"
    operator_prefix = f"{OPERATOR_START_TOKEN}{operator_name_to_define}"
    codex_prompt += operator_prefix
    try:
        completions = get_completions(
            codex_prompt, temperature=temperature, stop=STOP_TOKEN, n_samples=n_samples,
        )
        return codex_prompt, [operator_prefix + o for o in completions]
    except Exception as e:
        print(e)
        return codex_prompt, []


def propose_plans_for_problems(
    unsolved_problems,
    solved_problems,
    current_domain,
    supervision_pddl,
    max_supervision_examples=3,
    max_plan_examples=2,
    temperature=0.0,
    n_samples=1,
    verbose=False,
    output_directory=None,
    experiment_name="",
    use_mock=False,
):
    """
    Proposes PDDL plans given NL goals.
    Samples from: 
    P(pddl_plan | nl_goal, solved pddl_plan+nl_goal pairs)

    unsolved_problems:
        list of Problem objects to be solved
    solved_problems:
        list of Problem objects with solutions
    current_domain:
        Domain object describing the domain
    supervision_pddl:
         If not empty, use these external pddl action sequences.

    Edits the unsolved problem objects - adds plans to the problem.proposed_pddl_plan list
    """
    output_json = {}
    experiment_tag = "" if len(experiment_name) < 1 else f"{experiment_name}_"
    output_filepath = f"{experiment_tag}codex_plans.json"
    if use_mock:
        mock_propose_plans_for_problems(
            output_filepath, unsolved_problems, output_directory
        )
        return
    # Codex prompt header.
    nl_header = (
        ";;;; Given natural language goals, predict a sequence of PDDL actions.\n"
    )

    # Add supervision.
    if len(supervision_pddl) > 1:
        supervision_examples = random.sample(
            list(supervision_pddl.keys()),
            min(max_supervision_examples, len(supervision_pddl)),
        )
        for domain_file in supervision_examples:
            nl_header += f"{NATURAL_LANGUAGE_GOAL_START}{supervision_pddl[domain_file]['NL_goal']}\n"
            nl_header += f"{PDDL_PLAN_START}\n"
            nl_header += f"{get_plan_string_from_supervision_pddl(supervision_pddl[domain_file])}"
            nl_header += f"{STOP_TOKEN}\n"

    shared_header = nl_header
    for idx, unsolved_problem in enumerate(unsolved_problems):
        if verbose:
            print(f"Now on problem {idx} / {len(unsolved_problems)} ... ")

        codex_prompt = shared_header
        # Codex prompt example natural language goals and plans.
        problem_examples = random.sample(
            solved_problems, min(len(solved_problems), max_plan_examples),
        )
        for problem_example in problem_examples:
            codex_prompt += f"{NATURAL_LANGUAGE_GOAL_START}{problem_example.language}\n"
            codex_prompt += f"{PDDL_PLAN_START}\n"
            codex_prompt += f"{get_plan_string_from_solved_problem(problem_example)}"
            codex_prompt += f"{STOP_TOKEN}\n"

        # Add the current problem.
        codex_prompt += f"{NATURAL_LANGUAGE_GOAL_START}{unsolved_problem.language}\n"
        codex_prompt += f"{PDDL_PLAN_START}\n"

        try:
            plan_strings = get_completions(
                codex_prompt, temperature=temperature, stop=STOP_TOKEN
            )
            for plan_string in plan_strings:
                unsolved_problem.proposed_pddl_plans.append(
                    PDDLPlan(plan_string=plan_string)
                )  # editing the problem

            output_json[unsolved_problem.problem_id] = {
                CODEX_PROMPT: codex_prompt,
                CODEX_OUTPUT: plan_strings,
            }
        except Exception as e:
            print(e)
            continue
    if verbose:
        num_proposed = [p for p in unsolved_problems if len(p.proposed_pddl_plans) >= 1]
        print(
            f"\npropose_plans_for_problems: proposed plans for {len(num_proposed)} / {len(unsolved_problems)}"
        )
    if output_directory:
        with open(os.path.join(output_directory, output_filepath), "w") as f:
            json.dump(output_json, f)


def mock_propose_plans_for_problems(
    output_filepath, unsolved_problems, output_directory
):
    with open(os.path.join(output_directory, output_filepath), "r") as f:
        output_json = json.load(f)
    print(
        f"Now in: mock_propose_plans_for_problems: from {os.path.join(output_directory, output_filepath)}"
    )
    for unsolved_problem in unsolved_problems:
        if unsolved_problem.problem_id in output_json:
            for plan_string in output_json[unsolved_problem.problem_id][CODEX_OUTPUT]:
                unsolved_problem.proposed_pddl_plans.append(
                    PDDLPlan(plan_string=plan_string)
                )
    print(
        f"\t Loaded a total of {len([p for p in unsolved_problems if len(p.proposed_pddl_plans) > 0])} plans for {len(unsolved_problems)} unsolved problems."
    )


def get_plan_string_from_supervision_pddl(supervision_pddl):
    plan = PDDLPlan(plan=supervision_pddl["operator_sequence"])
    return plan.plan_to_string(plan.plan)


def get_plan_string_from_solved_problem(problem):
    """
    problem:
        solved Problem object
    return:
        string to add to the codex input prompt
    """
    plan = (
        problem.ground_truth_pddl_plan
        if problem.should_supervise_pddl
        else problem.get_best_evaluated_pddl_plan()
    )
    return plan.plan_to_string(plan.plan)


def get_alfred_goal_prompt(domain, problem):
    """
    problem:
        PDDL.Problem object
    returns:
        prompt
    """
    domain_string = domain.domain_for_goal_prompting(
        problem.ground_truth_pddl_problem.ground_truth_pddl_problem_string
    )
    NL_goal = NATURAL_LANGUAGE_GOAL_START + "\n" + problem.language
    pddl_goal = (
        PDDL_GOAL_START
        + "\n"
        + problem.ground_truth_pddl_problem.ground_truth_goal
        + "\n"
        + STOP_TOKEN
    )
    return "\n\n".join([domain_string, NL_goal, pddl_goal])


def get_supervision_goal_prompt(supervision_pddl):
    prompt = ""
    for domain_file in supervision_pddl:
        domain = supervision_pddl[domain_file]["domain"]
        pddl_problem_string = supervision_pddl[domain_file]["pddl_problem_string"]
        domain_string = domain.domain_for_goal_prompting(pddl_problem_string)
        NL_goal = (
            NATURAL_LANGUAGE_GOAL_START
            + "\n"
            + supervision_pddl[domain_file]["NL_goal"]
        )
        pddl_goal = (
            PDDL_GOAL_START
            + "\n"
            + supervision_pddl[domain_file]["goal_pddl"]
            + "\n"
            + STOP_TOKEN
        )
        prompt += "\n\n".join([domain_string, NL_goal, pddl_goal])
    return prompt


def get_unsolved_goal_prompt(domain, problem):
    domain_string = domain.domain_for_goal_prompting(
        problem.ground_truth_pddl_problem.ground_truth_pddl_problem_string
    )
    NL_goal = NATURAL_LANGUAGE_GOAL_START + "\n" + problem.language
    return "\n\n".join([domain_string, NL_goal])


def mock_propose_goals_for_problems(
    output_filepath, unsolved_problems, output_directory, current_domain
):
    with open(os.path.join(output_directory, output_filepath), "r") as f:
        output_json = json.load(f)
    print(
        f"Now in: mock_propose_goals_for_problems: from {os.path.join(output_directory, output_filepath)}"
    )
    for p in unsolved_problems:
        if p.problem_id in output_json:
            p.proposed_pddl_goals.extend(output_json[p.problem_id][CODEX_OUTPUT])
    print(
        f"\t Loaded a total of {len([p for p in unsolved_problems if len(p.proposed_pddl_goals) > 0])} goals for {len(unsolved_problems)} unsolved problems."
    )
    return


def propose_goals_for_problems(
    unsolved_problems,
    solved_problems,
    current_domain,
    initial_pddl_predicates,
    supervision_pddl,
    experiment_name,
    temperature=0.0,
    use_mock=False,
    max_goal_examples=2,
    n_samples=1,
    verbose=False,
    output_directory=None,
    use_gt=False,
    print_every=2,
):
    """
    unsolved_problems:
        list of Problem objects to be solved
    solved_problems:
        list of Problem objects with ground truth plans
    current_domain:
        Domain object describing the domain

    Edits the unsolved problem objects - adds PDDL proposed goals to the problem.proposed_pddl_goals list
    """
    if use_gt:
        print("Using ground truth goals, skipping: propose_PDDL_goals_for_problems")
        return
    output_json = {}
    experiment_tag = "" if len(experiment_name) < 1 else f"{experiment_name}_"
    output_filepath = (
        f"{experiment_tag}codex_goals_{'_'.join(initial_pddl_predicates)}.json"
    )
    if use_mock:
        mock_propose_goals_for_problems(
            output_filepath, unsolved_problems, output_directory, current_domain
        )
        return

    if verbose:
        print(
            f"propose_goals_for_problems: proposing for {len(unsolved_problems)} operators."
        )

    nl_header = "\n;; Natural language goals and PDDL goals\n\n"
    prompt = nl_header

    # Add supervision from external prompts.
    if supervision_pddl:
        prompt += get_supervision_goal_prompt(supervision_pddl)
    n_solved = len(solved_problems)
    solved_to_prompt = random.sample(solved_problems, max_goal_examples)
    for solved_problem in solved_to_prompt:  # constructing the input prompt
        prompt += get_alfred_goal_prompt(current_domain, solved_problem)
    for idx, problem in enumerate(unsolved_problems):
        if verbose and idx % print_every == 0:
            print(
                f"propose_goals_for_problems: now on {idx} / {len(unsolved_problems)}"
            )

        # Add supervision from ALFRED goals.
        temp_prompt = prompt + get_unsolved_goal_prompt(current_domain, problem)
        try:
            goal_strings = get_completions(
                temp_prompt,
                temperature=temperature,
                stop=STOP_TOKEN,
                n_samples=n_samples,
            )
            output_json[problem.problem_id] = {
                CODEX_PROMPT: temp_prompt,
                CODEX_OUTPUT: goal_strings,
            }
            problem.proposed_pddl_goals.extend(goal_strings)  # editing the problem
        except Exception as e:
            print(e)
            continue
    if output_directory:
        with open(os.path.join(output_directory, output_filepath), "w") as f:
            json.dump(output_json, f)

