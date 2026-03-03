"""
Market Research Crew — Streamlit UI
Fixed: shell injection, XSS, file-handle leak, source-mutation anti-pattern,
       concurrency guard, start_time bug, cross-platform venv path, path traversal,
       blocking sleep, magic numbers, missing logging.
"""

import html
import logging
import os
import sys
import time
import subprocess
from pathlib import Path

import streamlit as st

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Research Crew",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #080B0F;
    color: #E8EAF0;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 10%, #0D2818 0%, #080B0F 50%);
}
h1, h2, h3, h4 { font-family: 'Space Mono', monospace; }

.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    color: #00FF88;
    letter-spacing: -2px;
    line-height: 1.1;
    margin: 0;
}
.hero-sub {
    font-size: 1.1rem;
    color: #6B7280;
    margin-top: 8px;
    font-weight: 300;
}
.hero-badge {
    display: inline-block;
    background: rgba(0,255,136,0.08);
    border: 1px solid rgba(0,255,136,0.2);
    color: #00FF88;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 16px;
    letter-spacing: 2px;
}
[data-testid="stTextInput"] input {
    background: #0F1419 !important;
    border: 1px solid #1E2A20 !important;
    border-radius: 12px !important;
    color: #E8EAF0 !important;
    font-size: 1rem !important;
    padding: 16px 20px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #00FF88 !important;
    box-shadow: 0 0 0 3px rgba(0,255,136,0.08) !important;
}
[data-testid="stButton"] > button {
    background: #00FF88 !important;
    color: #080B0F !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 16px 32px !important;
    width: 100% !important;
    letter-spacing: 1px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stButton"] > button:hover {
    background: #00CC6A !important;
    box-shadow: 0 8px 32px rgba(0,255,136,0.3) !important;
}
[data-testid="stButton"] > button:disabled {
    background: #1C2128 !important;
    color: #4B5563 !important;
    cursor: not-allowed !important;
}
.agent-card {
    background: #0D1117;
    border: 1px solid #1C2128;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.agent-card.done    { border-color: rgba(0,255,136,0.3);  background: rgba(0,255,136,0.04); }
.agent-card.running { border-color: rgba(255,200,0,0.4);  background: rgba(255,200,0,0.04); }
.agent-icon { font-size: 1.4rem; }
.agent-name { font-weight: 600; font-size: 0.9rem; color: #C9D1D9; }
.agent-status {
    margin-left: auto;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 999px;
}
.status-waiting { background: #1C2128;                  color: #6B7280; }
.status-running { background: rgba(255,200,0,0.15);     color: #FFC800; }
.status-done    { background: rgba(0,255,136,0.12);     color: #00FF88; }
.section-divider { border: none; border-top: 1px solid #1C2128; margin: 32px 0; }
.success-msg {
    background: rgba(0,255,136,0.08);
    border: 1px solid rgba(0,255,136,0.25);
    border-radius: 12px;
    padding: 16px 20px;
    color: #00FF88;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    margin: 16px 0;
}
.output-box {
    background: #0D1117;
    border: 1px solid #1C2128;
    border-radius: 12px;
    padding: 24px;
    font-size: 0.9rem;
    line-height: 1.7;
    color: #C9D1D9;
    min-height: 200px;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
AGENTS = [
    {"icon": "📊", "name": "Market Research Specialist",       "file": "market_research.md"},
    {"icon": "🕵️", "name": "Competitive Intelligence Analyst", "file": "competitive_intelligence.md"},
    {"icon": "👥", "name": "Customer Insights Researcher",     "file": "customer_insights.md"},
    {"icon": "🗺️", "name": "Product Strategy Advisor",         "file": "product_strategy.md"},
    {"icon": "📈", "name": "Business Analyst",                 "file": "business_analysis.md"},
]

TIMEOUT_SECONDS   = 900   # 15 minutes
POLL_INTERVAL_SEC = 4     # seconds between UI refresh while running

BASE_DIR     = Path(__file__).parent.resolve()
PROJECT_ROOT = (BASE_DIR / ".." / "..").resolve()
OUTPUT_DIR   = PROJECT_ROOT / "output"
MAIN_SCRIPT  = PROJECT_ROOT / "src" / "market_research_crew" / "main.py"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _venv_python() -> Path:
    """Return the virtualenv Python executable for the current platform."""
    if sys.platform == "win32":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def _safe_output_path(filename: str) -> Path:
    """
    Resolve OUTPUT_DIR / filename and guard against path traversal.
    Raises ValueError if the resolved path escapes OUTPUT_DIR.
    """
    resolved = (OUTPUT_DIR / filename).resolve()
    if not str(resolved).startswith(str(OUTPUT_DIR.resolve())):
        raise ValueError(f"Path traversal attempt blocked: {filename!r}")
    return resolved


def get_output(filename: str) -> str | None:
    """Read an agent output file safely. Returns None if not yet present."""
    try:
        path = _safe_output_path(filename)
    except ValueError:
        logger.warning("Blocked path traversal for filename=%r", filename)
        return None

    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("Could not read output file %s: %s", path, exc)
    return None


def clear_outputs() -> None:
    """Remove all previous agent output files and ensure OUTPUT_DIR exists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for agent in AGENTS:
        path = OUTPUT_DIR / agent["file"]
        if path.exists():
            try:
                path.unlink()
                logger.info("Deleted previous output: %s", path)
            except OSError as exc:
                logger.warning("Could not delete %s: %s", path, exc)


def start_crew_process(product_idea: str) -> subprocess.Popen | None:
    """
    Spawn the CrewAI process, passing the product idea via a command-line
    argument — never via string interpolation into executable code.
    Returns the Popen object so the caller can track it, or None on failure.
    """
    python_exe = _venv_python()
    if not python_exe.exists():
        st.error(
            f"Python executable not found at `{python_exe}`. "
            "Please check your virtual environment setup."
        )
        logger.error("venv Python not found: %s", python_exe)
        return None

    if not MAIN_SCRIPT.exists():
        st.error(f"Main script not found at `{MAIN_SCRIPT}`.")
        logger.error("Main script not found: %s", MAIN_SCRIPT)
        return None

    log_path = PROJECT_ROOT / "crew_log.txt"
    try:
        log_fh = log_path.open("w", encoding="utf-8")
    except OSError as exc:
        st.error(f"Cannot open log file: {exc}")
        logger.error("Log file open failed: %s", exc)
        return None

    try:
        proc = subprocess.Popen(
            [str(python_exe), str(MAIN_SCRIPT), "--product-idea", product_idea],
            cwd=str(PROJECT_ROOT),
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            close_fds=(sys.platform != "win32"),
        )
        logger.info(
            "Started crew process pid=%d for product_idea=%r", proc.pid, product_idea
        )
        st.session_state.log_fh = log_fh
        return proc
    except OSError as exc:
        log_fh.close()
        st.error(f"Failed to start crew process: {exc}")
        logger.exception("Popen failed")
        return None


def _close_log_fh() -> None:
    """Close the log file handle if it is still open."""
    fh = st.session_state.get("log_fh")
    if fh and not fh.closed:
        try:
            fh.close()
            logger.info("Closed crew log file handle.")
        except OSError as exc:
            logger.warning("Error closing log file handle: %s", exc)
    st.session_state.log_fh = None


def _process_still_running() -> bool:
    """Return True if a previously started process is still alive."""
    proc: subprocess.Popen | None = st.session_state.get("process")
    return proc is not None and proc.poll() is None


# ── Session State Initialisation ───────────────────────────────────────────────
# FIX: All keys initialized upfront so st.session_state.start_time never raises
#      AttributeError regardless of which code path runs first.
_DEFAULTS = {
    "running":      False,
    "completed":    False,
    "product_idea": "",
    "start_time":   None,   # ← was missing before; caused AttributeError
    "process":      None,
    "log_fh":       None,
}
for _key, _val in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-badge">POWERED BY CREWAI · GROQ · LLAMA 3.3 70B</div>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">Market Research<br/>Crew</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">5 autonomous AI agents generating comprehensive market research reports</p>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)


# ── Layout ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("#### 🎯 Product Idea")
    product_idea = st.text_input(
        "Product Idea",
        placeholder="e.g. AI-powered smart home assistant",
        key="input_product",
        label_visibility="collapsed",
        disabled=st.session_state.running,
    )

    run_clicked = st.button(
        "⚡ RUN RESEARCH CREW",
        disabled=st.session_state.running,
    )

    if run_clicked:
        idea = product_idea.strip()
        if not idea:
            st.error("Please enter a product idea first!")
        elif _process_still_running():
            st.warning("⚠️ A crew is already running. Please wait for it to finish.")
        else:
            clear_outputs()
            proc = start_crew_process(idea)
            if proc is not None:
                st.session_state.running      = True
                st.session_state.completed    = False
                st.session_state.product_idea = idea
                st.session_state.start_time   = time.monotonic()  # FIX: set before rerun
                st.session_state.process      = proc
                logger.info("Session started for idea=%r", idea)
                st.rerun()

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("#### 🤖 Agent Pipeline")

    files_done = [get_output(a["file"]) is not None for a in AGENTS]
    num_done   = sum(files_done)

    for i, agent in enumerate(AGENTS):
        if files_done[i]:
            card, label, badge = "done",    "✓ DONE",    "status-done"
        elif st.session_state.running and i == num_done:
            card, label, badge = "running", "⏳ RUNNING", "status-running"
        else:
            card, label, badge = "",        "WAITING",   "status-waiting"

        st.markdown(f"""
        <div class="agent-card {card}">
            <span class="agent-icon">{agent['icon']}</span>
            <span class="agent-name">{html.escape(agent['name'])}</span>
            <span class="agent-status {badge}">{label}</span>
        </div>""", unsafe_allow_html=True)

    # ── Polling loop (only active while running) ───────────────────────────────
    if st.session_state.running:
        # FIX: start_time is guaranteed to be set (not None) when running=True
        elapsed = time.monotonic() - st.session_state.start_time

        if num_done == len(AGENTS):
            # All agents finished successfully.
            st.session_state.running    = False
            st.session_state.completed  = True
            st.session_state.start_time = None  # FIX: reset after use
            _close_log_fh()
            logger.info("All agents completed for idea=%r", st.session_state.product_idea)
            st.rerun()

        elif not _process_still_running():
            # Process exited before all outputs were written — likely an error.
            st.session_state.running    = False
            st.session_state.start_time = None  # FIX: reset after use
            _close_log_fh()
            st.error(
                "⚠️ The crew process exited unexpectedly. "
                f"Check `crew_log.txt` in `{PROJECT_ROOT}` for details."
            )
            logger.error("Crew process exited early; num_done=%d/%d", num_done, len(AGENTS))
            st.rerun()

        elif elapsed > TIMEOUT_SECONDS:
            # Hard timeout — kill the process.
            proc: subprocess.Popen = st.session_state.process
            proc.terminate()
            st.session_state.running    = False
            st.session_state.start_time = None  # FIX: reset after use
            _close_log_fh()
            logger.warning("Crew timed out after %ds", TIMEOUT_SECONDS)
            st.error("⚠️ Crew timed out after 15 minutes. Check your API key or try again.")
            st.rerun()

        else:
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            st.info(f"⏱️ Running… {mins}m {secs}s elapsed")
            time.sleep(POLL_INTERVAL_SEC)
            st.rerun()

    if st.session_state.completed:
        # FIX: Escape user content before injecting into HTML to prevent XSS.
        safe_idea = html.escape(st.session_state.product_idea)
        st.markdown(
            f'<div class="success-msg">✓ Research complete for: {safe_idea}</div>',
            unsafe_allow_html=True,
        )


# ── Right Column: Reports ──────────────────────────────────────────────────────
with col2:
    st.markdown("#### 📋 Research Reports")

    if num_done > 0:
        tab_labels = [f"{a['icon']} {a['name'].split()[0]}" for a in AGENTS]
        tabs = st.tabs(tab_labels)

        for i, (tab, agent) in enumerate(zip(tabs, AGENTS)):
            with tab:
                content = get_output(agent["file"])
                if content:
                    st.markdown(content)
                    st.download_button(
                        label="⬇️ Download Report",
                        data=content,
                        file_name=agent["file"],
                        mime="text/markdown",
                        key=f"dl_{i}",
                    )
                else:
                    st.markdown(
                        '<div class="output-box">Waiting for agent to complete…</div>',
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown("""
        <div class="output-box" style="display:flex;align-items:center;justify-content:center;
             color:#2D3748;font-family:'Space Mono',monospace;font-size:0.85rem;">
            Enter a product idea and run the crew to see reports here
        </div>""", unsafe_allow_html=True)