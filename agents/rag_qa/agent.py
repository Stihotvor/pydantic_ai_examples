# RAG QA agent equipped with the vector store.
import logging
import os
import uuid

from agents.rag_qa.knowledge import search, add_text

logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv

load_dotenv()

from pydantic_ai import Agent, ModelSettings, RunContext

agent = Agent(
    model=os.getenv("MODEL_STRING"),
    model_settings=ModelSettings(timeout=60),
    retries=3,
    instructions="You are a document Q&A assistant. "
                 "When users provide documents, store them. "
                 "When they ask questions, retrieve relevant context to answer. ",
)


@agent.tool
async def retrieve(ctx: RunContext, query: str, top_k: int = 3) -> str:
    """Retrieve the top k relevant documents based on a query.

    Args:
        query (str): The query to retrieve the top k relevant documents for.
        top_k (int): The number of documents to retrieve.
    """
    results = search(query, top_k)
    if not results:
        return "No matching documents found."

    return "\n\n---\n\n".join(results)


@agent.tool
async def store_document(ctx: RunContext, title: str, content: str) -> str:
    """Store a document in the vector store for semantic search.

    Args:
        title (str): The title of the document.
        content (str): The content of the document.
    """
    content = f"# {title}\n\n{content}"
    document_id = str(uuid.uuid4())
    add_text(content, document_id)
    return f"Document '{title}' stored successfully with ID: {document_id}"


app = agent.to_web()
