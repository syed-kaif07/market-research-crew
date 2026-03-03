#!/usr/bin/env python
"""
main.py — Entry point for the Market Research Crew.

Usage:
    # From the Streamlit UI (passes idea as a CLI argument):
    python main.py --product-idea "AI-powered smart home assistant"

    # Direct / manual run (falls back to --product-idea or prompts):
    python main.py --product-idea "gen ai in education"
"""

import argparse
import logging
import sys
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from market_research_crew.crew import MarketResearchCrew

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── CLI ────────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Market Research CrewAI pipeline for a given product idea.",
    )
    parser.add_argument(
        "--product-idea",
        type=str,
        default=None,
        help="The product idea to research (e.g. 'AI-powered smart home assistant').",
    )
    return parser.parse_args()


# ── Runner ─────────────────────────────────────────────────────────────────────
def run(product_idea: str) -> None:
    """
    Kick off the crew with the given product idea.
    Raises RuntimeError on failure so callers get a clean error type.
    """
    inputs = {"product_idea": product_idea}
    logger.info("Starting Market Research Crew for product_idea=%r", product_idea)

    try:
        MarketResearchCrew().crew().kickoff(inputs=inputs)
        logger.info("Crew completed successfully for product_idea=%r", product_idea)
    except Exception as exc:
        logger.exception("Crew run failed for product_idea=%r", product_idea)
        raise RuntimeError(f"An error occurred while running the crew: {exc}") from exc


# ── Entrypoint ─────────────────────────────────────────────────────────────────
def main() -> None:
    args = parse_args()

    product_idea = args.product_idea

    # If not provided via CLI, ask interactively (useful for manual runs).
    if not product_idea:
        try:
            product_idea = input("Enter a product idea to research: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.", file=sys.stderr)
            sys.exit(1)

    if not product_idea:
        print("Error: product idea cannot be empty.", file=sys.stderr)
        sys.exit(1)

    try:
        run(product_idea)
    except RuntimeError as exc:
        logger.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()