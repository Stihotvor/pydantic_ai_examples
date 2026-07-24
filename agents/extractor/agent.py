# Data extraction agent equipped with the structured output ability.
import logging
import os

logging.basicConfig(level=logging.INFO)
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

from pydantic_ai import Agent, ModelSettings


class ExtractedField(BaseModel):
    label: str
    value: str
    confidence: str  # high / medium / low


class ExtractionResult(BaseModel):
    title: str
    summary: str
    fields: List[ExtractedField]
    source_type: str | None = None


class ExtractionFailure(BaseModel):
    reason: str

    def __str__(self) -> str:
        return f"Extraction failed: {self.reason}"


agent = Agent(
    model=os.getenv("MODEL_STRING"),
    model_settings=ModelSettings(timeout=60),
    retries=3,
    instructions="Extract structured information from the provided text. "
                 "Identify the source type (article, email, report, etc.), "
                 "extract key fields with confidence levels (high/medium/low). "
                 "If the text is empty, gibberish, or not extractable, "
                 "return ExtractionFailure with the reason."
)


@agent.tool
def extract(ctx, title: str, summary: str, source_type: str, fields_json: str) -> str:
    """Extract structured information from the provided text.

    Args:
        title (str): The title of the document.
        summary (str): A brief summary of the document.
        source_type (str): The type of the source document.
        fields_json: FLAT JSON array of objects. Each object MUST have EXACTLY three keys:
            "label" (short field name), "value" (the extracted value as string),
            "confidence" (one of: high, medium, low).

            Example: [{"label": "Name", "value": "John", "confidence": "high"}]
            Do NOT nest objects inside values.

    Returns:
        str: The extracted information or a failure reason.
    """
    import json
    data = {
        "title": title,
        "summary": summary,
        "source_type": source_type,
        "fields": json.loads(fields_json)
    }
    return json.dumps(data, indent=2)


app = agent.to_web()
