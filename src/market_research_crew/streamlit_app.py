import streamlit as st
import os
import sys
import time
import subprocess

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Research Crew",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
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
h1, h2, h3 { font-family: 'Space Mono', monospace; }

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
}
[data-testid="stButton"] > button:hover {
    background: #00CC6A !important;
    box-shadow: 0 8px 32px rgba(0,255,136,0.3) !important;
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
.agent-card.done { border-color: rgba(0,255,136,0.3); background: rgba(0,255,136,0.04); }
.agent-card.running { border-color: rgba(255,200,0,0.4); background: rgba(255,200,0,0.04); }
.agent-icon { font-size: 1.4rem; }
.agent-name { font-weight: 600; font-size: 0.9rem; color: #C9D1D9; }
.agent-status {
    margin-left: auto;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 999px;
}
.status-waiting { background: #1C2128; color: #6B7280; }
.status-running { background: rgba(255,200,0,0.15); color: #FFC800; }
.status-done { background: rgba(0,255,136,0.12); color: #00FF88; }
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

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "output")
MAIN_PY      = os.path.join(BASE_DIR, "main.py")
# ── Helpers ────────────────────────────────────────────────────────────────────
def get_output(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def clear_outputs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for a in AGENTS:
        p = os.path.join(OUTPUT_DIR, a["file"])
        if os.path.exists(p):
            os.remove(p)

def update_main_py(product_idea):
    """Update product_idea in main.py before running."""
    with open(MAIN_PY, "r", encoding="utf-8") as f:
        content = f.read()
    import re
    content = re.sub(
        r'"product_idea":\s*"[^"]*"',
        f'"product_idea": "{product_idea}"',
        content
    )
    with open(MAIN_PY, "w", encoding="utf-8") as f:
        f.write(content)

def start_crew_process(product_idea):
    update_main_py(product_idea)
    python_exe = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    main_script = os.path.join(PROJECT_ROOT, "src", "market_research_crew", "main.py")
    
    subprocess.Popen(
        [python_exe, "-c", f"""
import sys
sys.path.insert(0, r'{os.path.join(PROJECT_ROOT, "src")}')
from market_research_crew.crew import MarketResearchCrew
MarketResearchCrew().crew().kickoff(inputs={{"product_idea": "{product_idea}"}})
"""],
        cwd=PROJECT_ROOT,
        stdout=open(os.path.join(PROJECT_ROOT, "crew_log.txt"), "w"),
        stderr=subprocess.STDOUT
    )

# ── Session State ──────────────────────────────────────────────────────────────
for key, val in [("running", False), ("completed", False), ("product_idea", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-badge">POWERED BY CREWAI · GROQ · LLAMA 3.3 70B</div>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">Market Research<br/>Crew</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">5 autonomous AI agents generating comprehensive market research reports</p>', unsafe_allow_html=True)
st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

# ── Layout ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("#### 🎯 Product Idea")
    product_idea = st.text_input(
        "Product Idea",
        placeholder="e.g. AI-powered smart home assistant",
        key="input_product",
        label_visibility="collapsed"
    )

    run_clicked = st.button("⚡ RUN RESEARCH CREW", disabled=st.session_state.running)

    if run_clicked and product_idea.strip():
        st.session_state.running      = True
        st.session_state.completed    = False
        st.session_state.product_idea = product_idea.strip()
        clear_outputs()
        start_crew_process(product_idea.strip())
        st.rerun()
    elif run_clicked:
        st.error("Please enter a product idea first!")

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
            <span class="agent-name">{agent['name']}</span>
            <span class="agent-status {badge}">{label}</span>
        </div>""", unsafe_allow_html=True)

    # Auto-refresh while running
    if st.session_state.running:
        if num_done == len(AGENTS):
            st.session_state.running   = False
            st.session_state.completed = True
            st.rerun()
        else:
            time.sleep(4)
            st.rerun()

    if st.session_state.completed:
        st.markdown(f'<div class="success-msg">✓ Research complete for: {st.session_state.product_idea}</div>', unsafe_allow_html=True)

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
                        key=f"dl_{i}"
                    )
                else:
                    st.markdown('<div class="output-box">Waiting for agent to complete...</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="output-box" style="display:flex;align-items:center;justify-content:center;
             color:#2D3748;font-family:'Space Mono',monospace;font-size:0.85rem;">
            Enter a product idea and run the crew to see reports here
        </div>""", unsafe_allow_html=True)