"""
Bloyce's Protocol — Downside Up Complaint Bureau
Streamlit graphical interface for the LangGraph complaint processor.  
"""

import os
import time
from datetime import datetime
from typing import List, Optional, TypedDict

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

# ──────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bloyce's Protocol | Downside Up Bureau",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# CUSTOM CSS — retro-bureaucratic, dark, amber-on-black
# ──────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Courier+Prime:wght@400;700&display=swap');

:root {
    --amber:   #FFB000;
    --amber-d: #CC8800;
    --red:     #FF3B30;
    --green:   #34C759;
    --bg:      #0A0A0A;
    --bg2:     #111111;
    --bg3:     #1A1A1A;
    --border:  #2A2A2A;
    --text:    #E0C97F;
    --muted:   #665533;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Courier Prime', monospace !important;
}

[data-testid="stSidebar"] {
    background-color: var(--bg2) !important;
    border-right: 1px solid var(--border);
}

h1, h2, h3, h4 {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--amber) !important;
    letter-spacing: 0.05em;
}

/* Header */
.bureau-header {
    text-align: center;
    padding: 2rem 0 1rem;
    border-bottom: 2px solid var(--amber);
    margin-bottom: 2rem;
}
.bureau-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.2rem;
    color: var(--amber);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 0;
}
.bureau-subtitle {
    font-size: 0.85rem;
    color: var(--muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}

/* Workflow step pills */
.step-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.3rem;
    flex-wrap: wrap;
    margin: 1.5rem 0;
}
.step-pill {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    padding: 0.25rem 0.7rem;
    border-radius: 2px;
    border: 1px solid var(--border);
    color: var(--muted);
    background: var(--bg3);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.step-pill.active  { border-color: var(--amber); color: var(--amber); background: #1A1200; }
.step-pill.done    { border-color: var(--green);  color: var(--green);  background: #0A1A0A; }
.step-pill.failed  { border-color: var(--red);    color: var(--red);    background: #1A0A0A; }
.step-arrow { color: var(--muted); font-size: 0.8rem; }

/* Category badge */
.cat-badge {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    padding: 0.2rem 0.6rem;
    border-radius: 2px;
    text-transform: uppercase;
}
.cat-portal      { background:#001A2A; color:#00AAFF; border:1px solid #00AAFF; }
.cat-monster     { background:#1A000A; color:#FF3B30; border:1px solid #FF3B30; }
.cat-psychic     { background:#100020; color:#BF5FFF; border:1px solid #BF5FFF; }
.cat-environmental { background:#001A00; color:#34C759; border:1px solid #34C759; }
.cat-other       { background:#1A1400; color:#FFB000; border:1px solid #FFB000; }

/* Result cards */
.result-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-left: 3px solid var(--amber);
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.88rem;
}
.result-card.rejected { border-left-color: var(--red); }
.result-card.closed   { border-left-color: var(--green); }

.field-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}
.field-value {
    color: var(--text);
    line-height: 1.5;
}

/* Buttons */
.stButton > button {
    font-family: 'Share Tech Mono', monospace !important;
    background: transparent !important;
    color: var(--amber) !important;
    border: 1px solid var(--amber) !important;
    border-radius: 2px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: var(--amber) !important;
    color: var(--bg) !important;
}

/* Text area */
.stTextArea textarea {
    background: var(--bg2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    font-family: 'Courier Prime', monospace !important;
    font-size: 0.9rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 1px var(--amber) !important;
}

/* Text input */
.stTextInput input {
    background: var(--bg2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    font-family: 'Courier Prime', monospace !important;
}

/* Selectbox */
.stSelectbox select, [data-baseweb="select"] {
    background: var(--bg2) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}

/* Progress / spinner */
.stSpinner > div { border-top-color: var(--amber) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--amber); }

/* Log box */
.log-box {
    background: #050505;
    border: 1px solid var(--border);
    padding: 0.8rem 1rem;
    font-size: 0.78rem;
    line-height: 1.6;
    max-height: 280px;
    overflow-y: auto;
    white-space: pre-wrap;
    color: #777;
    font-family: 'Share Tech Mono', monospace;
}

/* Effectiveness badge */
.eff-high   { color: var(--green); font-weight: bold; }
.eff-medium { color: var(--amber); font-weight: bold; }
.eff-low    { color: var(--red);   font-weight: bold; }

/* Divider */
.amber-divider { border: 0; border-top: 1px solid var(--border); margin: 1.5rem 0; }

/* History item */
.hist-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0.8rem;
    margin: 0.3rem 0;
    background: var(--bg3);
    border: 1px solid var(--border);
    font-size: 0.8rem;
    cursor: pointer;
    border-radius: 2px;
}
.hist-item:hover { border-color: var(--amber); }
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────
# STATE  (singleton per session)
# ──────────────────────────────────────────────────────────

if "history" not in st.session_state:
    st.session_state.history = []      # list of processed results
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "log_lines" not in st.session_state:
    st.session_state.log_lines = []
if "llm" not in st.session_state:
    st.session_state.llm = None

# ──────────────────────────────────────────────────────────
# LANGGRAPH COMPLAINT STATE
# ──────────────────────────────────────────────────────────

class ComplaintState(TypedDict):
    complaint: str
    category: str
    missing_details: List[str]
    is_valid: bool
    validation_notes: str
    evidence: str
    investigation_summary: str
    resolution: str
    effectiveness_rating: str
    requires_escalation: bool
    closed_at: str
    outcome: str
    follow_up_required: bool
    workflow_path: List[str]
    status: str
    rejection_reason: Optional[str]


# ──────────────────────────────────────────────────────────
# NODE FUNCTIONS
# ──────────────────────────────────────────────────────────

VALIDATION_RULES = {
    "portal": "must reference specific location or timing anomalies",
    "monster": "must describe creature behaviour or interactions",
    "psychic": "must reference specific ability limitations or malfunctions",
    "environmental": "must connect to electricity, weather, or observable physical phenomena",
    "other": "automatically escalated — no further validation required",
}

INVESTIGATION_FOCUS = {
    "portal": "temporal patterns, location consistency, and environmental factors",
    "monster": "behavioural data, interaction patterns, and environmental triggers",
    "psychic": "ability specifications, tested limitations, and contextual factors",
    "environmental": "power line activity, atmospheric conditions, and anomaly correlation",
    "other": "general context, stakeholders affected, and potential impact",
}

ESCALATION_CATEGORIES = {"environmental", "monster"}


def _log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.log_lines.append(f"[{ts}] {msg}")


def intake_node(state: ComplaintState) -> ComplaintState:
    _log("INTAKE — categorising complaint...")
    llm = st.session_state.llm

    cat_prompt = (
        "Categorise the complaint into exactly one of: "
        "portal, monster, psychic, environmental, other.\n\n"
        f"Complaint: {state['complaint']}\n\n"
        "Reply with ONLY the single category word."
    )
    category = llm.invoke([HumanMessage(content=cat_prompt)]).content.strip().lower()
    if category not in {"portal", "monster", "psychic", "environmental", "other"}:
        category = "other"

    detail_prompt = (
        "Check this complaint for required fields: who, what, when, where.\n"
        "List any that are MISSING. If all present, reply 'none'.\n\n"
        f"Complaint: {state['complaint']}\n\n"
        "Reply: comma-separated missing fields, or 'none'."
    )
    raw = llm.invoke([HumanMessage(content=detail_prompt)]).content.strip().lower()
    missing = [] if raw == "none" else [d.strip() for d in raw.split(",")]

    _log(f"INTAKE — category={category}, missing={missing or 'nothing'}")
    return {
        **state,
        "category": category,
        "missing_details": missing,
        "workflow_path": state.get("workflow_path", []) + ["intake"],
        "status": "intake_complete",
    }


def validate_node(state: ComplaintState) -> ComplaintState:
    _log("VALIDATE — applying protocol rules...")
    llm = st.session_state.llm

    if state.get("missing_details"):
        reason = f"Missing required details: {', '.join(state['missing_details'])}"
        _log(f"VALIDATE — REJECTED: {reason}")
        return {
            **state,
            "is_valid": False,
            "validation_notes": reason,
            "rejection_reason": reason,
            "workflow_path": state["workflow_path"] + ["validate"],
            "status": "rejected",
        }

    if state["category"] == "other":
        _log("VALIDATE — 'other' auto-escalated")
        return {
            **state,
            "is_valid": True,
            "validation_notes": "Auto-escalated: 'other' category requires manual review",
            "workflow_path": state["workflow_path"] + ["validate"],
            "status": "validated",
            "requires_escalation": True,
        }

    rule = VALIDATION_RULES[state["category"]]
    val_prompt = (
        f"Category rule for '{state['category']}': the complaint {rule}.\n\n"
        f"Complaint: {state['complaint']}\n\n"
        "Does this complaint satisfy the rule?\n"
        "Line 1: 'valid' or 'invalid'\nLine 2: one-sentence explanation."
    )
    lines = llm.invoke([HumanMessage(content=val_prompt)]).content.strip().splitlines()
    verdict = lines[0].strip().lower()
    notes = lines[1].strip() if len(lines) > 1 else ""
    is_valid = verdict == "valid"

    _log(f"VALIDATE — {'VALID' if is_valid else 'INVALID'}: {notes}")
    return {
        **state,
        "is_valid": is_valid,
        "validation_notes": notes,
        "rejection_reason": None if is_valid else f"Validation failed: {notes}",
        "workflow_path": state["workflow_path"] + ["validate"],
        "status": "validated" if is_valid else "rejected",
    }


def investigate_node(state: ComplaintState) -> ComplaintState:
    _log("INVESTIGATE — gathering evidence...")
    llm = st.session_state.llm
    focus = INVESTIGATION_FOCUS.get(state["category"], "general context")

    inv_prompt = (
        f"You are a field investigator for the Downside Up Complaint Bureau.\n"
        f"Category: {state['category']}\nFocus on: {focus}\n"
        f"Complaint: {state['complaint']}\n\n"
        "Write a structured report with:\n"
        "1. EVIDENCE GATHERED (bullet points)\n"
        "2. INVESTIGATION SUMMARY (2–3 sentences)"
    )
    full = llm.invoke([HumanMessage(content=inv_prompt)]).content.strip()

    evidence = full
    summary = ""
    if "INVESTIGATION SUMMARY" in full:
        parts = full.split("INVESTIGATION SUMMARY")
        evidence = parts[0].strip()
        summary = parts[1].strip().lstrip(":").strip()

    _log("INVESTIGATE — evidence collected")
    return {
        **state,
        "evidence": evidence,
        "investigation_summary": summary or full[:300],
        "workflow_path": state["workflow_path"] + ["investigate"],
        "status": "investigated",
    }


def resolve_node(state: ComplaintState) -> ComplaintState:
    _log("RESOLVE — generating resolution...")
    llm = st.session_state.llm

    res_prompt = (
        f"Category: {state['category']}\n"
        f"Complaint: {state['complaint']}\n"
        f"Investigation summary:\n{state['investigation_summary']}\n\n"
        "Provide:\n"
        "RESOLUTION: <one action sentence>\n"
        "PROTOCOL: <Downside Up procedure name>\n"
        "EFFECTIVENESS: HIGH | MEDIUM | LOW\n"
        "RATIONALE: <one sentence>"
    )
    raw = llm.invoke([HumanMessage(content=res_prompt)]).content.strip()

    resolution = effectiveness = ""
    for line in raw.splitlines():
        if line.startswith("RESOLUTION:"):
            resolution = line.replace("RESOLUTION:", "").strip()
        elif line.startswith("EFFECTIVENESS:"):
            effectiveness = line.replace("EFFECTIVENESS:", "").strip().lower()

    if effectiveness not in {"high", "medium", "low"}:
        effectiveness = "medium"

    requires_escalation = (
        state["category"] in ESCALATION_CATEGORIES or state.get("requires_escalation", False)
    )
    _log(f"RESOLVE — effectiveness={effectiveness.upper()}, escalate={requires_escalation}")
    return {
        **state,
        "resolution": resolution or raw,
        "effectiveness_rating": effectiveness,
        "requires_escalation": requires_escalation,
        "workflow_path": state["workflow_path"] + ["resolve"],
        "status": "resolved",
    }


def close_node(state: ComplaintState) -> ComplaintState:
    _log("CLOSE — logging outcome...")
    llm = st.session_state.llm

    close_prompt = (
        f"Complaint: {state['complaint']}\nResolution: {state['resolution']}\n\n"
        "Write a one-sentence satisfaction confirmation for the complainant, "
        "then on a new line write: RESOLVED, PARTIALLY_RESOLVED, or ESCALATED."
    )
    lines = llm.invoke([HumanMessage(content=close_prompt)]).content.strip().splitlines()
    outcome = "RESOLVED"
    for line in lines:
        l = line.strip().upper()
        if l in {"RESOLVED", "PARTIALLY_RESOLVED", "ESCALATED"}:
            outcome = l
            break

    if state.get("requires_escalation"):
        outcome = "ESCALATED"

    follow_up = state.get("effectiveness_rating") == "low"
    closed_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    _log(f"CLOSE — outcome={outcome}, follow_up={follow_up}")
    return {
        **state,
        "closed_at": closed_at,
        "outcome": outcome,
        "follow_up_required": follow_up,
        "workflow_path": state["workflow_path"] + ["close"],
        "status": "closed",
    }


def rejection_node(state: ComplaintState) -> ComplaintState:
    _log(f"REJECTED — {state.get('rejection_reason', 'unknown')}")
    return {
        **state,
        "workflow_path": state["workflow_path"] + ["rejected"],
        "status": "rejected",
    }


def route_after_validate(state: ComplaintState) -> str:
    return "investigate" if state.get("is_valid") else "rejected"


@st.cache_resource
def build_graph():
    wf = StateGraph(ComplaintState)
    wf.add_node("intake", intake_node)
    wf.add_node("validate", validate_node)
    wf.add_node("investigate", investigate_node)
    wf.add_node("resolve", resolve_node)
    wf.add_node("close", close_node)
    wf.add_node("rejected", rejection_node)
    wf.set_entry_point("intake")
    wf.add_edge("intake", "validate")
    wf.add_conditional_edges(
        "validate",
        route_after_validate,
        {"investigate": "investigate", "rejected": "rejected"},
    )
    wf.add_edge("investigate", "resolve")
    wf.add_edge("resolve", "close")
    wf.add_edge("close", END)
    wf.add_edge("rejected", END)
    return wf.compile()


# ──────────────────────────────────────────────────────────
# UI HELPERS
# ──────────────────────────────────────────────────────────

SAMPLE_COMPLAINTS = {
    "— select a sample —": "",
    "🌀 Portal timing anomaly": (
        "The Downside Up portal at Hawkins Lab opens at different times each day. "
        "Yesterday it opened at 3 AM, today at 11 PM. How do I predict when it will appear next?"
    ),
    "👾 Demogorgon behaviour": (
        "Demogorgons near the Byers' house sometimes work together to flush out prey, "
        "but last Tuesday they started attacking each other. What triggers this change?"
    ),
    "🧠 Psychic weight ceiling": (
        "Eleven can move objects with her mind but cannot lift anything heavier than ~20 kg. "
        "She has been practising daily at Hawkins lab since Monday. Why is there a weight ceiling?"
    ),
    "⚡ Power line interference": (
        "Every time a creature crosses over near Maple Street, the power lines buzz and "
        "streetlights flicker for exactly 4 minutes. Is there a physical cause for this?"
    ),
    "❌ Invalid (missing details)": (
        "Things in the Upside Down are weird and I don't like it. Fix it please."
    ),
}

CAT_COLOURS = {
    "portal": "cat-portal",
    "monster": "cat-monster",
    "psychic": "cat-psychic",
    "environmental": "cat-environmental",
    "other": "cat-other",
}

CAT_ICONS = {
    "portal": "🌀",
    "monster": "👾",
    "psychic": "🧠",
    "environmental": "⚡",
    "other": "📋",
}

WORKFLOW_STEPS = ["intake", "validate", "investigate", "resolve", "close"]


def render_step_pills(path: List[str], is_rejected: bool):
    pills_html = '<div class="step-row">'
    for i, step in enumerate(WORKFLOW_STEPS):
        if step in path:
            css = "done" if not (is_rejected and step == "validate") else "failed"
            if is_rejected and step == "validate":
                css = "failed"
        else:
            css = "pending"
        pills_html += f'<span class="step-pill {css}">{step}</span>'
        if i < len(WORKFLOW_STEPS) - 1:
            pills_html += '<span class="step-arrow">›</span>'
    if is_rejected:
        pills_html += '<span class="step-arrow">›</span><span class="step-pill failed">rejected</span>'
    pills_html += "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)


def render_result_card(result: dict):
    cat = result.get("category", "other")
    is_rejected = result.get("status") == "rejected"
    card_class = "rejected" if is_rejected else "closed"

    cat_html = (
        f'<span class="cat-badge {CAT_COLOURS.get(cat, "cat-other")}">'
        f'{CAT_ICONS.get(cat, "📋")} {cat}</span>'
    )

    render_step_pills(result.get("workflow_path", []), is_rejected)

    st.markdown(
        f'<div class="result-card {card_class}">'
        f'<div class="field-label">Category</div>'
        f'<div class="field-value">{cat_html}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    if is_rejected:
        st.markdown(
            f'<div class="result-card rejected">'
            f'<div class="field-label">❌ Rejection Reason</div>'
            f'<div class="field-value">{result.get("rejection_reason", "Unknown")}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    # Resolution
    eff = result.get("effectiveness_rating", "medium")
    eff_class = f"eff-{eff}"
    st.markdown(
        f'<div class="result-card closed">'
        f'<div class="field-label">Resolution</div>'
        f'<div class="field-value">{result.get("resolution", "—")}</div>'
        f'<br><div class="field-label">Effectiveness</div>'
        f'<div class="field-value"><span class="{eff_class}">{eff.upper()}</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    outcome = result.get("outcome", "RESOLVED")
    escalated = result.get("requires_escalation", False)
    follow_up = result.get("follow_up_required", False)
    closed_at = result.get("closed_at", "—")

    flags = []
    if escalated:
        flags.append("⚠️ Escalated to specialist team")
    if follow_up:
        flags.append("📅 30-day follow-up checkpoint scheduled")

    flags_html = "<br>".join(flags) if flags else "None"

    st.markdown(
        f'<div class="result-card closed">'
        f'<div class="field-label">Outcome</div><div class="field-value">{outcome}</div>'
        f'<br><div class="field-label">Flags</div><div class="field-value">{flags_html}</div>'
        f'<br><div class="field-label">Closed At</div><div class="field-value">{closed_at}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    with st.expander("📋 Investigation Report"):
        st.markdown(result.get("evidence", "—"))

    with st.expander("📝 Validation Notes"):
        st.markdown(result.get("validation_notes", "—"))


# ──────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "")

    user_key = st.text_input(
        "OpenAI API Key",
        value=api_key,
        type="password",
        help="Set OPENAI_API_KEY in a .env file or paste it here",
        placeholder="sk-...",
    )

    if user_key:
        if st.session_state.llm is None or getattr(st.session_state.llm, "openai_api_key", None) != user_key:
            st.session_state.llm = ChatOpenAI(
                model="gpt-4o-mini", temperature=0, api_key=user_key
            )
        st.success("API key loaded ✓", icon="🔑")
    else:
        st.warning("Enter your OpenAI API key to proceed.")

    st.markdown("<hr class='amber-divider'>", unsafe_allow_html=True)
    st.markdown("### 📜 Bloyce's Protocol Rules")
    with st.expander("Category definitions"):
        st.markdown(
            """
- **portal** — Portal timing, location, or behaviour  
- **monster** — Creature behaviour or interactions  
- **psychic** — Psychic ability limitations  
- **environmental** — Electricity, weather, physical env  
- **other** — Anything else (auto-escalated)
"""
        )
    with st.expander("Workflow rules"):
        st.markdown(
            """
- Intake → Validate → Investigate → Resolve → Close  
- No step can be skipped  
- Missing details (who/what/when/where) → rejected  
- Environmental & monster complaints → escalated  
- Low effectiveness → 30-day follow-up  
"""
        )

    st.markdown("<hr class='amber-divider'>", unsafe_allow_html=True)
    st.markdown("### 🗂️ Complaint History")

    if st.session_state.history:
        for i, h in enumerate(reversed(st.session_state.history)):
            cat = h.get("category", "other")
            status = h.get("status", "—")
            icon = "✅" if status == "closed" else "❌"
            snippet = h.get("complaint", "")[:35]
            if st.button(
                f"{icon} {CAT_ICONS.get(cat,'📋')} {snippet}...",
                key=f"hist_{i}",
                use_container_width=True,
            ):
                st.session_state.current_result = h
    else:
        st.caption("No complaints processed yet.")

    if st.session_state.history:
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.history = []
            st.session_state.current_result = None
            st.rerun()


# ──────────────────────────────────────────────────────────
# MAIN PANEL
# ──────────────────────────────────────────────────────────

st.markdown(
    """
<div class="bureau-header">
  <div class="bureau-title">🌀 Bloyce's Protocol</div>
  <div class="bureau-subtitle">Downside Up Complaint Bureau · Structured Processing System · Lab 2</div>
</div>
""",
    unsafe_allow_html=True,
)

col_form, col_result = st.columns([1, 1], gap="large")

with col_form:
    st.markdown("#### 📥 Submit Complaint")

    sample_key = st.selectbox(
        "Load sample complaint",
        options=list(SAMPLE_COMPLAINTS.keys()),
        index=0,
    )
    sample_text = SAMPLE_COMPLAINTS[sample_key]

    complaint_text = st.text_area(
        "Complaint text",
        value=sample_text,
        height=200,
        placeholder="Describe your Downside Up issue in detail. Include who, what, when, and where.",
    )

    submitted = st.button("⚡ PROCESS COMPLAINT", use_container_width=True)

    st.markdown("<hr class='amber-divider'>", unsafe_allow_html=True)
    st.markdown("#### 🖥️ Processing Log")
    log_placeholder = st.empty()


def render_log():
    lines = "\n".join(st.session_state.log_lines[-30:]) if st.session_state.log_lines else "Awaiting complaint..."
    log_placeholder.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)


render_log()

with col_result:
    st.markdown("#### 📤 Result")

    if submitted:
        if not st.session_state.llm:
            st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
        elif not complaint_text.strip():
            st.warning("Please enter a complaint.")
        else:
            st.session_state.log_lines = []
            _log("New complaint received")
            graph = build_graph()

            initial: ComplaintState = {
                "complaint": complaint_text.strip(),
                "category": "",
                "missing_details": [],
                "is_valid": False,
                "validation_notes": "",
                "evidence": "",
                "investigation_summary": "",
                "resolution": "",
                "effectiveness_rating": "",
                "requires_escalation": False,
                "closed_at": "",
                "outcome": "",
                "follow_up_required": False,
                "workflow_path": [],
                "status": "pending",
                "rejection_reason": None,
            }

            with st.spinner("Processing through Bloyce's Protocol..."):
                result = graph.invoke(initial)

            st.session_state.current_result = result
            st.session_state.history.append(result)
            _log("Workflow complete.")
            render_log()

    if st.session_state.current_result:
        render_result_card(st.session_state.current_result)
    else:
        st.markdown(
            '<div class="result-card" style="color:var(--muted);text-align:center;padding:3rem;">'
            "Submit a complaint to see the processed result here."
            "</div>",
            unsafe_allow_html=True,
        )
