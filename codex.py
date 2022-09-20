import openai
import os
from time import sleep

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


def propose_operator_names():
    ## TODO (cw/nk): propose operator names from a set of natural language plans and existing operator / domain definitions.
    pass


def propose_operator_definitions():
    ## TODO (cw/nk): propose operator body definitions from a set of natural language plans and existing operator / domain definitions.
    pass
