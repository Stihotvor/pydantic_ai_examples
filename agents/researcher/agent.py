# Web research agent equipped with web search tools.
import logging
import os

logging.basicConfig(level=logging.INFO)
from dotenv import load_dotenv

load_dotenv()

from firecrawl import Firecrawl
from pydantic_ai import Agent, ModelSettings

firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

agent = Agent(
    model=os.getenv("MODEL_STRING"),
    model_settings=ModelSettings(timeout=60),
    instructions="You are a research assistant..."
)


@agent.tool
def web_search(ctx, query: str, max_results: int = 5) -> str:
    """Search the web for current information on a topic."""
    results = firecrawl.search(query, limit=max_results)
    return "\n\n".join(
        f"Title: {r.title}\nURL: {r.url}\n{r.description or ''}"
        for r in (results.web or [])
    )


@agent.tool
def web_fetch(ctx, url: str) -> str:
    """Fetch the content of a web page."""
    doc = firecrawl.scrape(url, formats=["markdown"])
    return doc.markdown or str(doc)


app = agent.to_web()
