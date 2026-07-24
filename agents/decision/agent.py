import logging
import os

logging.basicConfig(level=logging.INFO)
from dotenv import load_dotenv

load_dotenv()

from pydantic_ai import Agent, ModelSettings, RunContext

agent = Agent(
    model=os.environ["MODEL_STRING"],
    model_settings=ModelSettings(timeout=60),
    retries=3,
    instructions="Analyze the user's decision question, "
                 "identify viable options with pros and cons, "
                 "score each option (1-10), assess risk levels, "
                 "and provide a clear recommendation.",
)


@agent.tool
def decide(ctx: RunContext, question: str, options_json: str,
           top_recommendation: str, reasoning: str, key_tradeoff: str) -> str:
    """Analyze a decision question and provide a structured recommendation.

    Args:
        question: The user's decision question
        options_json: JSON array of options, each with "name", "pros", "cons",
                     "score" (1-10), "risk_level" (low/medium/high)
        top_recommendation: The name of the recommended option
        reasoning: Detailed explanation of the recommendation
        key_tradeoff: The main trade-off in this decision
    """
    import json
    output = {
        "question": question,
        "options": json.loads(options_json),
        "top_recommendation": top_recommendation,
        "reasoning": reasoning,
        "key_tradeoff": key_tradeoff,
    }
    return json.dumps(output, indent=2)


app = agent.to_web()
