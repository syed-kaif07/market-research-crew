#!/usr/bin/env python
"""
main.py - Entry point for the Market Research Crew.
Streams live colored agent banners to the IDE terminal.
When triggered from Streamlit UI, both the terminal and UI update simultaneously.

Usage:
    python main.py --product-idea "AI-powered smart home assistant"
    python main.py --product-idea "gen ai in education"
"""

import argparse
import logging
import sys
import time
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from market_research_crew.crew import MarketResearchCrew

# ANSI Colors
class C:
    RESET  = "\033[0m";  BOLD   = "\033[1m"
    GREEN  = "\033[92m"; YELLOW = "\033[93m"
    CYAN   = "\033[96m"; RED    = "\033[91m"
    WHITE  = "\033[97m"; DIM    = "\033[2m"

# Agent list — order must match tasks in crew.py
AGENTS = [
    {"icon": "📊", "name": "Market Research Specialist"},
    {"icon": "🕵️", "name": "Competitive Intelligence Analyst"},
    {"icon": "👥", "name": "Customer Insights Researcher"},
    {"icon": "🗺️", "name": "Product Strategy Advisor"},
    {"icon": "📈", "name": "Business Analyst"},
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Terminal print helpers

def _div(char="-", w=65, col=C.DIM):
    print(f"{col}{char * w}{C.RESET}", flush=True)

def _banner(idea: str):
    print(flush=True)
    _div("=", 65, C.CYAN)
    print(f"{C.BOLD}{C.CYAN}{'  MARKET RESEARCH CREW - AGENT PIPELINE':^65}{C.RESET}", flush=True)
    print(f"{C.DIM}{'  Powered by CrewAI x Groq x LLaMA 3.3 70B':^65}{C.RESET}", flush=True)
    _div("=", 65, C.CYAN)
    print(f"\n  {C.BOLD}Research Topic:{C.RESET} {C.CYAN}{idea}{C.RESET}", flush=True)
    print(f"  {C.DIM}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}\n", flush=True)

def _print_queue():
    print(f"{C.BOLD}{C.WHITE}  AGENT PIPELINE QUEUE:{C.RESET}\n", flush=True)
    for i, a in enumerate(AGENTS, 1):
        print(f"  {C.DIM}{i}.{C.RESET} {a['icon']}  {C.WHITE}{a['name']}{C.RESET}  {C.DIM}[ QUEUED ]{C.RESET}", flush=True)
    print(flush=True)
    _div()
    print(flush=True)

def _agent_start(idx: int):
    a = AGENTS[idx - 1]
    print(flush=True)
    _div("-", 65, C.YELLOW)
    print(f"  {C.BOLD}{C.YELLOW}>> AGENT {idx}/{len(AGENTS)} STARTING{C.RESET}  {a['icon']}  {C.BOLD}{C.WHITE}{a['name']}{C.RESET}", flush=True)
    print(f"  {C.DIM}Time: {datetime.now().strftime('%H:%M:%S')}{C.RESET}", flush=True)
    _div("-", 65, C.YELLOW)
    print(flush=True)

def _agent_done(idx: int, elapsed: float):
    a     = AGENTS[idx - 1]
    total = len(AGENTS)
    bar   = f"{C.GREEN}{'█' * idx}{C.RESET}{C.DIM}{'░' * (total - idx)}{C.RESET}"
    print(flush=True)
    _div("-", 65, C.GREEN)
    print(f"  {C.BOLD}{C.GREEN}✓ AGENT {idx}/{total} COMPLETE{C.RESET}  {a['icon']}  {C.BOLD}{C.WHITE}{a['name']}{C.RESET}", flush=True)
    print(f"  {C.DIM}Time taken: {elapsed:.1f}s{C.RESET}", flush=True)
    print(f"  Progress: [{bar}] {C.BOLD}{C.GREEN}{idx}/{total}{C.RESET}", flush=True)
    _div("-", 65, C.GREEN)
    print(flush=True)

def _crew_complete(elapsed: float, idea: str):
    print(flush=True)
    _div("=", 65, C.GREEN)
    print(f"{C.BOLD}{C.GREEN}{'  ALL AGENTS COMPLETE - RESEARCH DONE!':^65}{C.RESET}", flush=True)
    _div("=", 65, C.GREEN)
    print(f"\n  {C.DIM}Topic  :{C.RESET} {C.WHITE}{idea}{C.RESET}", flush=True)
    print(f"  {C.DIM}Time   :{C.RESET} {C.WHITE}{elapsed:.1f}s ({elapsed/60:.1f} min){C.RESET}", flush=True)
    print(f"  {C.DIM}Reports:{C.RESET} {C.CYAN}output/{C.RESET}\n", flush=True)
    _div("=", 65, C.GREEN)
    print(flush=True)

def _crew_error(exc: Exception):
    print(flush=True)
    _div("=", 65, C.RED)
    print(f"{C.BOLD}{C.RED}{'  CREW FAILED - CHECK LOGS':^65}{C.RESET}", flush=True)
    _div("=", 65, C.RED)
    print(f"\n  {C.RED}{exc}{C.RESET}\n", flush=True)


# Task tracker — hooks into CrewAI's task_callback

class _TaskTracker:
    def __init__(self):
        self.done        = 0
        self.agent_start = time.monotonic()
        self.crew_start  = time.monotonic()

    def on_task_complete(self, task_output):
        """
        Called automatically by CrewAI after every task finishes.
        Prints agent done banner and starts the next agent banner.
        """
        try:
            self.done  += 1
            elapsed     = time.monotonic() - self.agent_start
            _agent_done(self.done, elapsed)
            self.agent_start = time.monotonic()
            if self.done < len(AGENTS):
                _agent_start(self.done + 1)
        except Exception:
            pass  # Never crash the crew due to logging


# CLI

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Market Research Crew with live terminal logging.",
    )
    parser.add_argument(
        "--product-idea",
        type=str,
        default=None,
        help="The product idea to research.",
    )
    return parser.parse_args()


# Runner

def run(product_idea: str) -> None:
    tracker = _TaskTracker()

    _banner(product_idea)
    _print_queue()
    _agent_start(1)   # Show Agent 1 starting immediately

    logger.info("Starting Market Research Crew for product_idea=%r", product_idea)

    try:
        crew_obj = MarketResearchCrew().crew()
        crew_obj.task_callback = tracker.on_task_complete   # live terminal hook

        crew_obj.kickoff(inputs={"product_idea": product_idea})

        _crew_complete(time.monotonic() - tracker.crew_start, product_idea)
        logger.info("Crew completed successfully for product_idea=%r", product_idea)

    except Exception as exc:
        _crew_error(exc)
        logger.exception("Crew run failed for product_idea=%r", product_idea)
        raise RuntimeError(f"An error occurred while running the crew: {exc}") from exc


# Entrypoint

def main() -> None:
    args = parse_args()
    product_idea = args.product_idea

    if not product_idea:
        try:
            print(f"\n{C.CYAN}  Enter a product idea to research:{C.RESET} ", end="", flush=True)
            product_idea = input().strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.RED}  Aborted.{C.RESET}", file=sys.stderr)
            sys.exit(1)

    if not product_idea:
        print(f"{C.RED}  Error: product idea cannot be empty.{C.RESET}", file=sys.stderr)
        sys.exit(1)

    try:
        run(product_idea)
    except RuntimeError as exc:
        logger.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()