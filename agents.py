from dataclasses import dataclass
from types import SimpleNamespace
import os

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - fallback when openai isn't available
    OpenAI = None

@dataclass
class Agent:
    name: str
    instructions: str
    model: str = "gpt-4o"

class Runner:
    """Simple wrapper to execute an agent synchronously."""

    @staticmethod
    def run_sync(agent: Agent, input: str):
        if OpenAI is None:
            return SimpleNamespace(final_output="OpenAI library not installed.")
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=agent.model,
            messages=[
                {"role": "system", "content": agent.instructions},
                {"role": "user", "content": input},
            ],
        )
        return SimpleNamespace(final_output=response.choices[0].message.content)
