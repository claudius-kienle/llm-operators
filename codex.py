import code

import planning_domain
import openai
import os
from time import sleep
import random

random.seed(0)

OPERATOR_START = ";; Operator: "
EXAMPLE_START = ";; Example: "
OPERATOR_START_TOKEN = "(:action "
OPERATOR_STOP_TOKEN = ";; END OPERATOR"

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY is not set. Please set this in the shell via `export OPENAI_API_KEY=...`"
    )
openai.api_key = os.environ["OPENAI_API_KEY"]


def get_completions(prompt, temperature, stop, n_samples=1):
    response = openai.Completion.create(
        engine="code-davinci-002",
        prompt=prompt,
        temperature=0.1,
        max_tokens=800,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=stop,
        n=n_samples,
    )
    return [c["text"] for c in response.choices]


def propose_operator_uses():
    ## TODO (cw/nk): propose operator names from a set of natural language plans and existing operator / domain definitions.
    # See prior implementation: prototype_main.py -- get_proposed_plans_codex
    pass


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
        codex_prompt += f"{OPERATOR_STOP_TOKEN}\n"

    # Codex prompt for operator definition.
    codex_prompt += f"{OPERATOR_START}{operator_name_to_define}\n"
    if operator_name_to_define in operator_uses:
        for use_example in operator_uses[operator_name_to_define]:
            codex_prompt += f"{EXAMPLE_START}{use_example}\n"
    operator_prefix = f"{OPERATOR_START_TOKEN}{operator_name_to_define}"
    codex_prompt += operator_prefix

    completions = get_completions(
        codex_prompt,
        temperature=temperature,
        stop=OPERATOR_STOP_TOKEN,
        n_samples=n_samples,
    )
    return [operator_prefix + o for o in completions]
