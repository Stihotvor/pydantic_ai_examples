# Flight broker agent.
import logging
import os

from firecrawl import Firecrawl

logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

from pydantic_ai import Agent, ModelSettings, RunContext, UsageLimits


# Models
class FlightDetails(BaseModel):
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str  # ISO 8601 format
    arrival_time: str  # ISO 8601 format
    price: float
    currency: str


class NoFlightFound(BaseModel):
    reason: str


class SeatPreference(BaseModel):
    row: int = Field(ge=1, le=30, description="The seat preference row.")
    seat: str  # A-F


# Settings
firecrawl = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
USAGE_LIMITS = UsageLimits(request_limit=15)

# Agents
main_agent = Agent(
    model=os.getenv("MODEL_STRING"),
    model_settings=ModelSettings(timeout=60),
    retries=3,
    instructions="You are a flight booking assistant.",
)

flight_search_agent = Agent(
    model=os.getenv("MODEL_STRING"),
    name="flight_search",
    model_settings=ModelSettings(timeout=60),
    output_type=FlightDetails | NoFlightFound,
    retries=3,
    instructions="Use the firecrawl_search tool to find flights, "
                 "then return the best match.",
)

seat_agent = Agent(
    model=os.getenv("MODEL_STRING"),
    model_settings=ModelSettings(timeout=60),
    output_type=SeatPreference | NoFlightFound,
    retries=3,
    instructions="Seats A and F are window seats. Row 1 has extra leg room.",
)


@main_agent.tool
async def search_flight(ctx: RunContext, departure_airport: str, arrival_airport: str, departure_date: str,
                        return_date: str | None = None) -> str:
    """Search for available flights based on user preferences."""
    result = await flight_search_agent.run(
        f"Find flights for {departure_airport=} {arrival_airport=} {departure_date=} {return_date=}",
        usage=ctx.usage,
        usage_limits=USAGE_LIMITS,
    )
    if isinstance(result.output, FlightDetails):
        f = result.output
        return f"{f.airline} flight {f.flight_number} from {f.departure_airport} to {f.arrival_airport} departs at {f.departure_time} and arrives at {f.arrival_time}. Price: {f.price} {f.currency}"

    return f"No flight found: {result.output.reason}"


@main_agent.tool
async def extract_seat(ctx: RunContext, preference: str) -> str:
    """Extract seat preference from user preferences."""
    result = await seat_agent.run(preference, usage=ctx.usage, usage_limits=USAGE_LIMITS)
    if isinstance(result.output, SeatPreference):
        s = result.output
        return f"Seat preference: Row {s.row}, Seat {s.seat}"
    return f"Unable to extract seat preference: {result.output.reason}"


@flight_search_agent.tool
async def firecrawl_search(ctx: RunContext, origin: str, destination: str) -> str:
    """Search for flights from origin to destination."""
    results = firecrawl.search(f"flights {origin} to {destination}", limit=5)
    return "\n\n".join(
        f"{r.title}: {r.description or ''}"
        for r in (results.web or [])
    )


app = main_agent.to_web()
