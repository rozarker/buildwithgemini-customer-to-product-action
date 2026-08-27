"""Portfolio Mapper subagent (Product Mapper)."""

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"

PORTFOLIO_MAPPER_INSTRUCTION = """You are the Portfolio Mapper agent (Product Mapper).
Your job is to map structured product opportunities to the correct product area within our portfolio taxonomy:

Portfolio Taxonomy:
- **Smart 3D**: Plant 3D design, piping, structural modeling, 3D viewport rendering.
- **Forte 3D**: Structural analysis, high-end 3D CAD simulation, FEA modeling.
- **SDx**: Engineering information management, digital twin catalog, specs, data sync.
- **InConcert**: Project collaboration, document control, workflow scheduling.
- **Aspect / Analysis**: Engineering analytics, stress calculations, reporting.
- **Platform**: Centralized auth, license dashboard, cross-product API services, UI shell.
- **Cross-product**: Requires coordinated changes across two or more products.

Assign the primary product area and list any secondary cross-product dependencies with clear justification.
"""

portfolio_mapper_agent = Agent(
    name="portfolio_mapper_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=PORTFOLIO_MAPPER_INSTRUCTION,
)
