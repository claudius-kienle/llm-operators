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

STOP_TOKEN = "\n<END>\n"
OPERATOR_START = ";; Operator: "
EXAMPLE_START = ";; Example: "
OPERATOR_START_TOKEN = "(:action "
NL_PROMPT = "\n#### Natural language goals and PDDL plans\n\n"

# if not os.getenv("OPENAI_API_KEY"):
#     raise ValueError(
#         "OPENAI_API_KEY is not set. Please set this in the shell via `export OPENAI_API_KEY=...`"
#     )
# openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_key = "sk-kXXSnnSNUWZOfDHWRow4edlBSKjeQEFZ7wVASMzS"

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


def propose_plans_operators_goals_for_problems(
    current_domain, problems, n_samples=1, verbose=False
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
    # TODO: PROPOSE NEW OPERATOR GOALS.

    # TODO: NK

    # Propose new Codex plans.
    propose_plans_for_problems(
        unsolved_problems, solved_problems, current_domain, verbose=verbose
    )
    # Get all operator / actions from plans
    operator_uses = get_operator_uses(problems)

    # Propose definitions for any operators we haven't implemented.
    proposed_operators = [p for p in operator_uses if p not in current_domain.operators]
    proposed_operator_definitions = dict()
    for o in proposed_operators:
        propose_operator_definition(
            current_domain,
            o,
            operator_uses=operator_uses,
            max_operator_examples=10,
            temperature=0.0,
            n_samples=n_samples,
            verbose=verbose,
        )
    return proposed_operator_definitions


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


def get_solved_problem_text(problem):
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
    problem_text = (
        "#" + problem.language + "\n" + plan.plan_to_string(plan.plan) + STOP_TOKEN
    )
    return problem_text


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


def propose_plans_for_problems(
    unsolved_problems, solved_problems, current_domain, n_samples=1, verbose=False
):
    """
    unsolved_problems:
        list of Problem objects to be solved
    solved_problems:
        list of Problem objects with solutions
    current_domain:
        Domain object describing the domain

    Edits the unsolved problem objects - adds plans to the problem.proposed_pddl_plan list
    """
    if verbose:
        print("\npropose_plans_for_problems...")
    prompt = current_domain.to_string() + NL_PROMPT
    # TODO: randomly sample some problems for the prompt.
    for solved_problem in solved_problems:  # constructing the input prompt
        prompt += get_solved_problem_text(solved_problem)
    for problem in unsolved_problems:
        temp_prompt = prompt + "\n# " + problem.language
        try:
            plan_strings = get_completions(
                temp_prompt, temperature=0.1, stop=STOP_TOKEN
            )
            for plan_string in plan_strings:
                problem.proposed_pddl_plans.append(
                    PDDLPlan(plan_string=plan_string)
                )  # editing the problem
        except Exception as e:
            print(e)
            continue

    if verbose:
        num_proposed = [p for p in unsolved_problems if len(p.proposed_pddl_plans) > 1]
        print(
            f"\npropose_plans_for_problems: proposed plans for {len(num_proposed)} / {len(unsolved_problems)}"
        )


def propose_operator_definition(
    current_domain,
    operator_name_to_define,
    operator_uses={},
    max_operator_examples=10,
    temperature=0.0,
    n_samples=1,
    verbose=False,
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
    pddl_domain = (
        ";;;; PDDL domain definition.\n"
        + current_domain.domain_definition_to_string()
        + "\n\n"
    )
    translation_header = ";;;; Define operators based on examples of their usage and the PDDL domain definition above. Only use predicates and functions available in the PDDL domain.\n\n"

    codex_prompt = nl_header + pddl_domain + translation_header

    # Codex prompt exampler operators.
    operator_examples = random.sample(
        list(current_domain.operators.keys()),
        min(len(current_domain.operators), max_operator_examples),
    )
    for o in operator_examples:
        codex_prompt += f"{OPERATOR_START}{o}\n"
        if o in operator_uses:
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

    completions = get_completions(
        codex_prompt, temperature=temperature, stop=STOP_TOKEN, n_samples=n_samples,
    )
    return [operator_prefix + o for o in completions]
