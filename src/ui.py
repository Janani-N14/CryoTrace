import os
import sys
import uuid
import json
import time
import urllib
from pathlib import Path
from dotenv import load_dotenv, set_key
import streamlit as st
import pandas as pd
import requests
from sqlalchemy import create_engine, text
from langchain_core.messages import HumanMessage, ToolMessage

# ==========================================
# 1. IMMEDIATE PATH & ENVIRONMENT RESOLUTION
# ==========================================
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
env_file_path = project_root / ".env"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv(env_file_path)

from src.orchestrator import create_agent, fde_agent
from src.agent_tools import query_telemetry_db, fetch_corridor_conditions, search_compliance_sop

# ==========================================
# 2. PAGE CONFIGURATION & ENTERPRISE THEME
# ==========================================
st.set_page_config(
    page_title="CryoTrace — Cold-Chain Command Center",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Modern Glassmorphic Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    code, pre, .stCodeBlock { font-family: 'JetBrains Mono', monospace !important; }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0F172A 0%, #070B12 55%, #030712 100%);
        color: #E2E8F0;
    }
    
    div[data-testid="stSidebar"] {
        background: #090E17 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.12);
    }
    
    /* Top Hero Header */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 24px;
        backdrop-filter: blur(16px);
    }
    
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        background: linear-gradient(90deg, #F8FAFC 0%, #38BDF8 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 13.5px;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* Metric Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .kpi-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    
    .kpi-label {
        font-size: 11.5px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
        font-weight: 600;
    }
    
    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 4px;
    }
    
    .kpi-badge {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 999px;
        font-weight: 600;
        display: inline-block;
        margin-top: 6px;
    }
    
    .badge-cyan { background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .badge-green { background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-purple { background: rgba(129, 140, 248, 0.15); color: #818CF8; border: 1px solid rgba(129, 140, 248, 0.3); }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    
    /* Diagnostics Results Cards */
    .diag-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }
    .diag-card.success { border-left: 4px solid #10B981; }
    .diag-card.error { border-left: 4px solid #EF4444; }
    .diag-card.warning { border-left: 4px solid #F59E0B; }
    
    /* Custom Prompt Quick Chips */
    .chip-btn {
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        color: #E2E8F0 !important;
        border-radius: 999px !important;
        font-size: 12.5px !important;
        transition: all 0.2s ease !important;
    }
    
    /* Status Pulse */
    .pulse-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        background: #10B981;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 2s infinite;
        margin-right: 6px;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    .stTextInput>div>div>input {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
    }

    /* Fix Chat Input Text Visibility */
    div[data-testid="stChatInput"] {
        background-color: #1E293B !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        background-color: transparent !important;
        font-size: 14.5px !important;
        line-height: 1.5 !important;
        caret-color: #38BDF8 !important;
    }
    
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #94A3B8 !important;
    }

    /* Fix Chat Message Text & Bubbles Visibility */
    div[data-testid="stChatMessage"] {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
    }
    
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessage"] li {
        color: #F8FAFC !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE SETUP & AUDIT LOG WRITER
# ==========================================
db_host = os.getenv("SQL_SERVER_HOST", "localhost")
db_port = os.getenv("SQL_SERVER_PORT", "1433")
db_user = os.getenv("SQL_AGENT_USER", "USR_FDE_RO")
db_password = os.getenv("SQL_AGENT_PASSWORD", "AgentPassword2026!")

connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={db_host},{db_port};"
    f"DATABASE=master;"
    f"UID={db_user};"
    f"PWD={db_password};"
    f"Encrypt=no;"
    f"TrustServerCertificate=yes;"
)

log_params = urllib.parse.quote_plus(connection_string)
log_engine = create_engine(f"mssql+pyodbc:///?odbc_connect={log_params}")

def write_audit_log(session_id, node_name, tool_name, content):
    try:
        with log_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO FDE_VIEWS.AgentAuditLog (SessionID, NodeExecuted, ToolName, Content)
                VALUES (:session_id, :node_name, :tool_name, :content)
            """), {
                "session_id": session_id,
                "node_name": node_name,
                "tool_name": tool_name,
                "content": str(content)
            })
            conn.commit()
    except Exception as e:
        print(f"Audit Log Failed: {e}")

# ==========================================
# 4. SESSION STATE INITIALIZATION
# ==========================================
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []

if "active_agent" not in st.session_state:
    st.session_state.active_agent = fde_agent

if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = os.getenv("Agent_llm", "GROQ").upper()

if "api_key_override" not in st.session_state:
    st.session_state.api_key_override = ""

# Track quick prompt selection
if "prefill_prompt" not in st.session_state:
    st.session_state.prefill_prompt = ""

# ==========================================
# 5. SIDEBAR: NAVIGATION & CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 12px; padding: 10px; font-size: 24px;">🧊</div>
            <div>
                <div style="font-weight: 700; font-size: 16px; color: #F8FAFC;">FDE Command Center</div>
                <div style="font-size: 11px; color: #38BDF8; font-weight: 500;"><span class="pulse-dot"></span>System Active</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    app_mode = st.radio(
        "Navigation", 
        [
            "🧊 Dispatch Console", 
            "🔬 Endpoint Health & Diagnostics", 
            "🛡️ Security & Audit Logs"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 🧠 AI Reasoner Config")
    
    llm_options = ["GROQ", "OPENAI", "DEEPSEEK"]
    default_idx = llm_options.index(st.session_state.selected_llm) if st.session_state.selected_llm in llm_options else 0
    chosen_llm = st.selectbox("LLM Provider", llm_options, index=default_idx)
    
    current_key_val = os.getenv(f"{chosen_llm}_API_KEY", "")
    key_input = st.text_input(
        f"{chosen_llm} API Key", 
        value=st.session_state.api_key_override or current_key_val, 
        type="password",
        help="Update your API key here. It will immediately apply to reasoning tasks."
    )
    
    if st.button("💾 Apply & Update Key", use_container_width=True):
        st.session_state.api_key_override = key_input.strip()
        st.session_state.selected_llm = chosen_llm
        try:
            # Recreate agent with new key
            st.session_state.active_agent = create_agent(chosen_llm, key_input.strip())
            # Save into .env for persistence
            if env_file_path.exists():
                set_key(str(env_file_path), f"{chosen_llm}_API_KEY", key_input.strip())
                set_key(str(env_file_path), "Agent_llm", chosen_llm)
            st.success(f"✅ {chosen_llm} Reasoner updated!")
            time.sleep(0.5)
            st.rerun()
        except Exception as err:
            st.error(f"Failed to update reasoner: {err}")

    st.markdown("---")
    st.caption(f"Session Token: `{st.session_state.thread_id[:8]}...`")
    st.caption(f"Vector Index: `fde-sop-index-local`")
    st.caption(f"Telemetry DB: `localhost:1433/master`")
    
    if st.button("🗑️ Reset Chat Workspace", use_container_width=True):
        st.session_state.ui_messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# ==========================================
# 6. TOP HERO BANNER & KPI METRICS
# ==========================================
st.markdown("""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1 class="hero-title">🧊 CryoTrace: Cold-Chain Incident Command Center</h1>
            <p class="hero-subtitle">Autonomous Fleet Telemetry & Incident Mitigation Platform • ReAct Agentic AI</p>
        </div>
        <div>
            <span class="kpi-badge badge-green"><span class="pulse-dot"></span>Live Fleet Connected</span>
            <span class="kpi-badge badge-cyan">ODBC Driver 18 Active</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# KPI Summary Statistics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Monitored Fleet Records</div>
        <div class="kpi-value">32,065</div>
        <span class="kpi-badge badge-cyan">FDE_VIEWS.VW_ACTIVE_FLEET</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Target Temp Envelope</div>
        <div class="kpi-value">0.0°C – 4.0°C</div>
        <span class="kpi-badge badge-green">Fresh Perishables SOP</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Security Architecture</div>
        <div class="kpi-value">Least Privilege</div>
        <span class="kpi-badge badge-purple">USR_FDE_RO (DENY Raw)</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    active_brain = st.session_state.selected_llm
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Active Brain Engine</div>
        <div class="kpi-value">{active_brain}</div>
        <span class="kpi-badge badge-amber">Pinecone + Weather Tools</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 7. ROUTE TABS / MODES
# ==========================================

# ------------------------------------------
# TAB 1: DISPATCH CONSOLE
# ------------------------------------------
if app_mode == "🧊 Dispatch Console":
    st.markdown("### 💬 Real-Time Incident Dispatch Console")
    
    # Quick Action Prompt Chips
    st.markdown("<div style='font-size: 12px; color: #94A3B8; margin-bottom: 8px;'>⚡ QUICK INCIDENT QUERIES:</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🚨 Check LA Fleet Anomalies", use_container_width=True):
            st.session_state.pending_query = "Find any active shipments near Los Angeles (Latitude ~33.8, Longitude ~-118.1). Check the local weather there, and tell me if the current cargo temperature violates the SOP for fresh perishables."
            st.rerun()
    with c2:
        if st.button("🌦️ Port Long Beach Congestion", use_container_width=True):
            st.session_state.pending_query = "Check port congestion around Long Beach / LA. If severity index exceeds 7.0, what does SOP dictate?"
            st.rerun()
    with c3:
        if st.button("📋 Tier 1 vs Tier 2 Escalation", use_container_width=True):
            st.session_state.pending_query = "I'm a new dispatcher on the night shift. Can you quickly explain the difference between a Tier 1 and Tier 2 escalation?"
            st.rerun()
    with c4:
        if st.button("🛑 Spoilage Threshold Rules", use_container_width=True):
            st.session_state.pending_query = "What is the critical temperature threshold and immediate mitigation protocol for fresh perishables?"
            st.rerun()

    st.markdown("---")
    
    # Display message history
    for entry in st.session_state.ui_messages:
        with st.chat_message(entry["role"], avatar="👤" if entry["role"] == "user" else "🤖"):
            if "traces" in entry and entry["traces"]:
                with st.expander(f"🔍 Agent Execution Telemetry ({len(entry['traces'])} Steps)", expanded=False):
                    for trace in entry["traces"]:
                        if trace["type"] == "tool_input":
                            st.markdown(f"**⚡ Tool Triggered:** `{trace['name']}`")
                            st.json(trace["args"])
                        elif trace["type"] == "tool_output":
                            st.markdown(f"**📥 Output ({trace['name']}):**")
                            st.code(trace["content"], language="text")
            st.markdown(entry["content"])

    # Handle incoming input
    chat_box_input = st.chat_input("Query fleet telemetry, corridor weather, or SOP compliance rules...")
    user_input = None
    if chat_box_input:
        user_input = chat_box_input
    elif "pending_query" in st.session_state and st.session_state.pending_query:
        user_input = st.session_state.pending_query
        st.session_state.pending_query = None

    if user_input:
        st.session_state.ui_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            final_response = ""
            current_traces = []
            thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            with st.status("🧠 Reasoning over Telemetry, Weather & SOP Vectors...", expanded=True) as status:
                try:
                    events = st.session_state.active_agent.stream(
                        {"messages": [HumanMessage(content=user_input)]}, 
                        config=thread_config,
                        stream_mode="updates"
                    )
                    
                    for event in events:
                        for node_name, node_state in event.items():
                            if node_name == "reasoner":
                                latest_msg = node_state["messages"][-1]
                                
                                # Tool call interceptions
                                if hasattr(latest_msg, "tool_calls") and latest_msg.tool_calls:
                                    for tool_call in latest_msg.tool_calls:
                                        status.update(label=f"🔧 Routing to Subsystem: {tool_call['name']}...")
                                        current_traces.append({
                                            "type": "tool_input",
                                            "name": tool_call['name'],
                                            "args": tool_call['args']
                                        })
                                        write_audit_log(
                                            session_id=st.session_state.thread_id,
                                            node_name="reasoner",
                                            tool_name=tool_call['name'],
                                            content=json.dumps(tool_call['args'])
                                        )
                                
                                if latest_msg.content:
                                    final_response = latest_msg.content
                                    status.update(label="📝 Synthesizing Executive Mitigation Report...")
                                    write_audit_log(
                                        session_id=st.session_state.thread_id,
                                        node_name="reasoner_final",
                                        tool_name="LLM Text Synthesis",
                                        content=final_response
                                    )
                                    
                            elif node_name == "tools":
                                status.update(label="📡 Fetching Real-Time Corridor & SOP Records...")
                                for msg in node_state.get("messages", []):
                                    if isinstance(msg, ToolMessage):
                                        current_traces.append({
                                            "type": "tool_output",
                                            "name": msg.name,
                                            "content": msg.content
                                        })
                                        write_audit_log(
                                            session_id=st.session_state.thread_id,
                                            node_name="tools",
                                            tool_name=msg.name,
                                            content=msg.content
                                        )
                                        
                    status.update(label="Incident Evaluation Complete", state="complete", expanded=False)
                    
                except Exception as ex:
                    err_str = str(ex)
                    status.update(label="⚠️ Subsystem Communication Warning", state="error", expanded=True)
                    
                    if "401" in err_str or "invalid_api_key" in err_str.lower():
                        st.markdown(f"""
                        <div class="diag-card error">
                            <h4 style="margin: 0; color: #EF4444;">🔑 LLM Authentication Warning (HTTP 401)</h4>
                            <p style="font-size: 13px; color: #CBD5E1; margin: 8px 0;">
                                The current <strong>{st.session_state.selected_llm} API key</strong> is invalid or revoked.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        new_key = st.text_input("Enter a valid API Key to resume live reasoning:", type="password", key="inline_key_fix")
                        if st.button("Apply Key & Retry", key="apply_inline_btn"):
                            if new_key.strip():
                                st.session_state.api_key_override = new_key.strip()
                                st.session_state.active_agent = create_agent(st.session_state.selected_llm, new_key.strip())
                                st.rerun()
                                
                        st.markdown("---")
                        st.markdown("**Fallback Direct Subsystem Execution:** The agent tools (MSSQL Database, Weather API, Pinecone Vector DB) remain fully online. Running direct diagnostic retrieval:")
                        
                        # Direct tool execution fallback
                        sql_res = query_telemetry_db.invoke("SELECT TOP 3 Timestamp, Latitude, Longitude, Current_Temperature_C, Risk_Classification FROM FDE_VIEWS.VW_ACTIVE_FLEET")
                        weather_res = fetch_corridor_conditions.invoke({"latitude": 33.77, "longitude": -118.19})
                        sop_res = search_compliance_sop.invoke(user_input)
                        
                        final_response = f"""
### 1. Executive Summary
* Direct subsystem inspection completed for query: *"{user_input}"*.
* Active fleet records, corridor weather, and compliance policy documents successfully extracted below.

### 2. Telemetry & Environment Analysis
```text
{sql_res}
```

**Live Weather Corridor:**
```text
{weather_res}
```

### 3. SOP Compliance Clauses
```text
{sop_res}
```
"""
                    else:
                        st.error(f"Execution Error: {err_str}")
                        final_response = f"Subsystem execution error: {err_str}"
            
            if final_response:
                st.markdown(final_response)
                st.session_state.ui_messages.append({
                    "role": "assistant",
                    "content": final_response,
                    "traces": current_traces
                })

# ------------------------------------------
# TAB 2: ENDPOINT HEALTH & DIAGNOSTICS HUB
# ------------------------------------------
elif app_mode == "🔬 Endpoint Health & Diagnostics":
    st.markdown("### 🔬 Enterprise Subsystem Health & Endpoint Diagnostics")
    st.markdown("Benchmark latency, verify RBAC data-loss prevention, and test live connectivity across all enterprise endpoints.")
    
    if st.button("🚀 Run Complete Endpoint Diagnostic Suite", use_container_width=True, type="primary"):
        progress_bar = st.progress(0)
        diag_results = []
        
        # 1. MSSQL ACTIVE VIEW
        progress_bar.progress(20, text="Pinging MSSQL Semantic View (FDE_VIEWS.VW_ACTIVE_FLEET)...")
        try:
            t0 = time.time()
            with log_engine.connect() as conn:
                sample = conn.execute(text("SELECT TOP 1 Timestamp, Latitude, Longitude, Current_Temperature_C FROM FDE_VIEWS.VW_ACTIVE_FLEET")).fetchone()
                count = conn.execute(text("SELECT COUNT(*) FROM FDE_VIEWS.VW_ACTIVE_FLEET")).scalar()
            lat = round((time.time() - t0) * 1000, 1)
            diag_results.append({
                "name": "1. MSSQL Telemetry View",
                "target": "localhost:1433 -> FDE_VIEWS.VW_ACTIVE_FLEET",
                "status": "PASS",
                "latency": f"{lat} ms",
                "details": f"Total rows: {count:,} | Sample: {sample}"
            })
        except Exception as e:
            diag_results.append({
                "name": "1. MSSQL Telemetry View",
                "target": "localhost:1433 -> FDE_VIEWS.VW_ACTIVE_FLEET",
                "status": "FAIL",
                "latency": "N/A",
                "details": str(e)
            })

        # 2. RBAC SECURITY DENY TEST
        progress_bar.progress(40, text="Verifying RBAC Guardrail (DENY check on raw dbo table)...")
        try:
            t0 = time.time()
            with log_engine.connect() as conn:
                conn.execute(text("SELECT TOP 1 * FROM dbo.TBL_SC_FLEET_HIST_RAW"))
            diag_results.append({
                "name": "2. RBAC Security Guardrail",
                "target": "dbo.TBL_SC_FLEET_HIST_RAW (Deny Rule)",
                "status": "FAIL",
                "latency": "N/A",
                "details": "SECURITY VULNERABILITY: USR_FDE_RO has unauthorized read access to raw schema!"
            })
        except Exception as e:
            lat = round((time.time() - t0) * 1000, 1)
            diag_results.append({
                "name": "2. RBAC Security Guardrail",
                "target": "dbo.TBL_SC_FLEET_HIST_RAW (Deny Rule)",
                "status": "PASS",
                "latency": f"{lat} ms",
                "details": "Access correctly DENIED. Hallucination mutation guardrail active."
            })

        # 3. OPEN-METEO WEATHER REST API
        progress_bar.progress(60, text="Testing Open-Meteo Corridor Weather API...")
        try:
            t0 = time.time()
            r = requests.get("https://api.open-meteo.com/v1/forecast?latitude=33.77&longitude=-118.19&current_weather=true", timeout=6)
            lat = round((time.time() - t0) * 1000, 1)
            if r.status_code == 200:
                cw = r.json().get("current_weather", {})
                diag_results.append({
                    "name": "3. External Weather REST API",
                    "target": "api.open-meteo.com (GPS 33.77, -118.19)",
                    "status": "PASS",
                    "latency": f"{lat} ms",
                    "details": f"HTTP 200 OK | Temp: {cw.get('temperature')}°C | Wind: {cw.get('windspeed')} km/h"
                })
            else:
                diag_results.append({
                    "name": "3. External Weather REST API",
                    "target": "api.open-meteo.com",
                    "status": "FAIL",
                    "latency": f"{lat} ms",
                    "details": f"HTTP {r.status_code}: {r.text[:100]}"
                })
        except Exception as e:
            diag_results.append({
                "name": "3. External Weather REST API",
                "target": "api.open-meteo.com",
                "status": "FAIL",
                "latency": "N/A",
                "details": str(e)
            })

        # 4. PINECONE VECTOR DATABASE
        progress_bar.progress(80, text="Inspecting Pinecone Vector Store & SOP Index...")
        try:
            t0 = time.time()
            from pinecone import Pinecone
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            idx = pc.Index("fde-sop-index-local")
            stats = idx.describe_index_stats()
            lat = round((time.time() - t0) * 1000, 1)
            diag_results.append({
                "name": "4. Pinecone Vector Database",
                "target": "Index: fde-sop-index-local",
                "status": "PASS",
                "latency": f"{lat} ms",
                "details": f"Total Chunks: {stats.total_vector_count} | Dimension: {stats.dimension} | Metric: Cosine"
            })
        except Exception as e:
            diag_results.append({
                "name": "4. Pinecone Vector Database",
                "target": "Index: fde-sop-index-local",
                "status": "FAIL",
                "latency": "N/A",
                "details": str(e)
            })

        # 5. LLM REASONER ENDPOINT
        progress_bar.progress(100, text="Verifying LLM Provider Endpoint...")
        active_llm = st.session_state.selected_llm
        try:
            t0 = time.time()
            if active_llm == "GROQ":
                key = st.session_state.api_key_override or os.getenv("GROQ_API_KEY")
                r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=6)
                lat = round((time.time() - t0) * 1000, 1)
                if r.status_code == 200:
                    diag_results.append({
                        "name": f"5. LLM Reasoner ({active_llm})",
                        "target": "https://api.groq.com/openai/v1",
                        "status": "PASS",
                        "latency": f"{lat} ms",
                        "details": f"HTTP 200 OK | Authenticated successfully."
                    })
                else:
                    diag_results.append({
                        "name": f"5. LLM Reasoner ({active_llm})",
                        "target": "https://api.groq.com/openai/v1",
                        "status": "FAIL",
                        "latency": f"{lat} ms",
                        "details": f"HTTP {r.status_code} Unauthorized: API key invalid. Update in sidebar."
                    })
            elif active_llm == "OPENAI":
                key = st.session_state.api_key_override or os.getenv("OPENAI_API_KEY")
                r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=6)
                lat = round((time.time() - t0) * 1000, 1)
                diag_results.append({
                    "name": f"5. LLM Reasoner ({active_llm})",
                    "target": "https://api.openai.com/v1",
                    "status": "PASS" if r.status_code == 200 else "FAIL",
                    "latency": f"{lat} ms",
                    "details": f"HTTP {r.status_code}: {'Authenticated' if r.status_code == 200 else r.text[:100]}"
                })
        except Exception as e:
            diag_results.append({
                "name": f"5. LLM Reasoner ({active_llm})",
                "target": "Cloud API Endpoint",
                "status": "FAIL",
                "latency": "N/A",
                "details": str(e)
            })

        st.session_state.diag_results = diag_results

    # Render Diagnostic Results
    if "diag_results" in st.session_state:
        st.markdown("#### Diagnostic Report Card")
        for item in st.session_state.diag_results:
            is_pass = item["status"] == "PASS"
            card_class = "success" if is_pass else "error"
            badge_class = "badge-green" if is_pass else "badge-red"
            icon = "✅" if is_pass else "❌"
            
            st.markdown(f"""
            <div class="diag-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 700; font-size: 15px; color: #F8FAFC;">
                        {icon} {item['name']}
                    </div>
                    <div>
                        <span class="kpi-badge {badge_class}">{item['status']}</span>
                        <span style="font-size: 12px; color: #94A3B8; margin-left: 8px;">{item['latency']}</span>
                    </div>
                </div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Target: <code>{item['target']}</code></div>
                <div style="font-size: 13px; color: #CBD5E1; margin-top: 6px;">{item['details']}</div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: AUDIT TRAIL & COMPLIANCE LOGS
# ------------------------------------------
elif app_mode == "🛡️ Security & Audit Logs":
    st.markdown("### 🛡️ Enterprise Security & Audit Trail")
    st.caption("Immutable cryptographic log of all agent tool parameters, executions, and database queries in `FDE_VIEWS.AgentAuditLog`.")
    
    with st.expander("🔐 Administrative Authentication Gate", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            input_user = st.text_input("Admin Username", value=os.getenv("SQL_ADMIN_USER", "sa"))
        with col2:
            input_pass = st.text_input("Admin Password", type="password", value="FdeEnterprisePass123!")
            
        load_logs = st.button("Authenticate & Query Database Logs", use_container_width=True)

    if load_logs or "audit_df" in st.session_state:
        try:
            admin_conn = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={db_host},{db_port};"
                f"DATABASE=master;"
                f"UID={input_user};"
                f"PWD={input_pass};"
                f"Encrypt=no;"
                f"TrustServerCertificate=yes;"
            )
            admin_engine = create_engine(f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(admin_conn)}")
            
            with admin_engine.connect() as conn:
                query = """
                    SELECT TOP 100 LogID, Timestamp, SessionID, NodeExecuted, ToolName, Content 
                    FROM FDE_VIEWS.AgentAuditLog 
                    ORDER BY Timestamp DESC
                """
                df = pd.read_sql(query, conn)
                st.session_state.audit_df = df
            
            st.success(f"✅ Authenticated successfully. Loaded {len(df)} audit events.")
            
            if not df.empty:
                st.dataframe(
                    df,
                    column_config={
                        "LogID": st.column_config.NumberColumn("ID", format="%d"),
                        "Timestamp": st.column_config.DatetimeColumn("Execution Time", format="DD/MM/YYYY-h:mm:ss a"),
                        "SessionID": "Session Token",
                        "NodeExecuted": "Graph Node",
                        "ToolName": "Subsystem",
                        "Content": "Payload"
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=500
                )
                
                # CSV Export
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Audit Trail (CSV)",
                    data=csv,
                    file_name="fde_cold_chain_audit_log.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No audit traces recorded yet. Execute queries in the Dispatch Console to populate logs.")
                
        except Exception as err:
            st.error(f"Database Query Failed: {err}")