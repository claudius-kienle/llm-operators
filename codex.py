"""
codex.py 
Utilities that call a large language-code model.
"""
import time
import code
from collections import defaultdict

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
PDDL_PLAN_START = ";; PDDL Plan: "
OPERATOR_START_TOKEN = "(:action "
CODEX_PROMPT = "codex_prompt"
CODEX_OUTPUT = "codex_output"
NLgoals_PDDLplans_prompt = "\n#### Natural language goals and PDDL plans\n\n"
NLgoals_PDDLgoals_prompt = "\n#### Natural language goals and PDDL goals\n\n"

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY is not set. Please set this in the shell via `export OPENAI_API_KEY=...`"
    )
openai.api_key = os.environ["OPENAI_API_KEY"]


def propose_plans_operators_goals_for_problems(
    current_domain,
    problems,
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
        print("propose_plans_operators_goals_for_problems: ")
        print(
            f"{len(unsolved_problems)} unsolved problems / {len(solved_problems)} solved problems"
        )

    # Natural language goals to PDDL plans (operators + arguments) for unsolved problems.
    propose_plans_for_problems(
        unsolved_problems=unsolved_problems,
        solved_problems=solved_problems,
        current_domain=current_domain,
        n_samples=n_samples,
        temperature=temperature,
        verbose=verbose,
        output_directory=output_directory,
        use_mock=command_args.debug_mock_propose_plans,
    )
    # PDDL plans (operators + arguments) to operator definitions (pre/post predicates) for unsolved problems.
    propose_operators_for_problems(
        problems,
        current_domain,
        verbose,
        temperature,
        n_samples,
        output_directory,
        initial_pddl_predicates=command_args.initial_pddl_predicates,
        use_mock=command_args.debug_mock_propose_operators,
    )

    ### PDDL operators to new predicates for unsolved problems.
    propose_predicates_for_problems(
        problems=problems, current_domain=current_domain, use_mock=False,
    )

    # TODO: MAKE SURE we are not training on comments in the PDDL files.
    # Propose new PDDL goals
    propose_PDDL_goals_for_problems(unsolved_problems, solved_problems, current_domain)


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
    # Extract predicates from proposed operators.
    for o in current_domain.proposed_operators:
        for operator_definition in current_domain.proposed_operators[o]:
            import pdb

            pdb.set_trace()


def propose_operators_for_problems(
    problems,
    current_domain,
    verbose,
    temperature,
    n_samples,
    output_directory,
    initial_pddl_predicates,
    use_mock,
):
    output_json = {}
    output_filepath = f"codex_operators{'_'.join(initial_pddl_predicates)}.json"

    # What operators were proposed across the problems?
    operator_uses = get_operator_uses(problems)
    # Propose definitions for any operators we haven't implemented.
    proposed_operators = [p for p in operator_uses if p not in current_domain.operators]
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
    for o in proposed_operators:
        if o in output_json:
            current_domain.proposed_operators[o] = output_json[o][CODEX_OUTPUT]


def get_operator_uses(problems):
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
    return existing_operator_uses


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
    max_operator_examples=10,
    max_usage_examples=10,
    temperature=0.0,
    n_samples=1,
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
    nl_header = (
        ";;;; Define planning operators based on a PDDL domain and example usages.\n\n"
    )
    codex_prompt = nl_header
    if len(initial_pddl_predicates) < 0:
        pddl_domain = (
            ";;;; PDDL domain definition.\n"
            + current_domain.domain_definition_to_string()
            + "\n\n"
        )
        translation_header = ";;;; Define operators based on examples of their usage and the PDDL domain definition above. Only use predicates and functions available in the PDDL domain.\n\n"

        codex_prompt += pddl_domain + translation_header

    # Codex prompt exampler operators.
    operator_examples = random.sample(
        list(current_domain.operators.keys()),
        min(len(current_domain.operators), max_operator_examples),
    )
    for o in operator_examples:
        codex_prompt += f"{OPERATOR_START}{o}\n"
        if o in operator_uses:
            usage_examples = random.sample(
                list(operator_uses[o]), min(len(operator_uses[o]), max_usage_examples),
            )
            for use_example in operator_uses[o]:
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
    max_plan_examples=10,
    temperature=0.0,
    n_samples=1,
    verbose=False,
    output_directory=None,
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

    Edits the unsolved problem objects - adds plans to the problem.proposed_pddl_plan list
    """
    output_json = {}
    output_filepath = "codex_plans.json"
    if use_mock:
        mock_propose_plans_for_problems(
            output_filepath, unsolved_problems, output_directory
        )
        return
    # Codex prompt header.
    nl_header = ";;;; Semantic parsing from natural language goals into PDDL plans.\n"
    # Note that we do not actually use the current domain.
    shared_header = nl_header
    for unsolved_problem in unsolved_problems:
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
        num_proposed = [p for p in unsolved_problems if len(p.proposed_pddl_plans) > 1]
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
    for unsolved_problem in unsolved_problems:
        if unsolved_problem.problem_id in output_json:
            for plan_string in output_json[unsolved_problem.problem_id][CODEX_OUTPUT]:
                unsolved_problem.proposed_pddl_plans.append(
                    PDDLPlan(plan_string=plan_string)
                )


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


def get_supervised_goal_prompt(problem):
    """
    problem:
        PDDL.Problem object
    returns:
        string of NL goal + PDDL goal
    """
    NL_goal = "\n#" + problem.language + "\n"
    PDDL_goal = problem.ground_truth_pddl_problem.ground_truth_goal
    return NL_goal + PDDL_goal + STOP_TOKEN

def mock_propose_PDDL_goals_for_problems(output_filepath, unsolved_problems, output_directory, current_domain
):
    with open(os.path.join(output_directory, output_filepath), "r") as f:
        output_json = json.load(f)
    for p in unsolved_problems:
        if p.problem_id in output_json:
            p.proposed_pddl_goals.extend(output_json[p][CODEX_OUTPUT])
    return


def propose_PDDL_goals_for_problems(
    unsolved_problems,
    solved_problems,
    current_domain,
    initial_pddl_predicates,
    use_mock,
    n_samples=1,
    verbose=False,
    output_directory = '',
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
    prompt = current_domain.domain_definition_to_string() + NLgoals_PDDLgoals_prompt
    n_solved = len(solved_problems)
    solved_to_prompt = random.sample(solved_problems, n_solved//3 + 1)
    output_json = {}
    output_filepath = f"codex_PDDL_goals_{'_'.join(initial_pddl_predicates)}.json"
    if use_mock:
        mock_propose_PDDL_goals_for_problems(
            output_filepath, unsolved_problems, output_directory, current_domain)
        return
    for solved_problem in solved_to_prompt:  # constructing the input prompt
        prompt += get_supervised_goal_prompt(solved_problem)
    for problem in unsolved_problems:
        temp_prompt = prompt + "\n; " + problem.language
        try:
            goal_strings = get_completions(
                temp_prompt, temperature=0.1, stop=STOP_TOKEN
            )
            output_json[problem.problem_id] = {
                CODEX_PROMPT : temp_prompt,
                CODEX_OUTPUT : goal_strings
            }
            problem.proposed_pddl_goals.extend(goal_strings)  # editing the problem

        except Exception as e:
            print(e)
            continue
    if output_directory:
        with open(os.path.join(output_directory, output_filepath), "w") as f:
            json.dump(output_json, f)