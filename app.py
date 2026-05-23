import streamlit as st
import time
import json
import os
import random

# Graceful import for Google Cloud Dialogflow CX
try:
    from google.cloud import dialogflowcx_v3 as df_cx
    from google.api_core.exceptions import GoogleAPICallError
    CX_SUPPORTED = True
except ImportError:
    CX_SUPPORTED = False

# --- Page Layout Configuration ---
st.set_page_config(
    page_title="ResearchForge AI — Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Pure White Corporate Minimalist Theme CSS Injection ---
st.markdown("""
<style>
    /* Clean System/Inter Typography Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    /* Core Typography & Pure White Variables */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #ffffff;
    }
    ::-webkit-scrollbar-thumb {
        background: #e5e5e5;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #cccccc;
    }
    
    .stCodeBlock, code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
    }

    /* Minimalist Corporate Clean Header */
    .header-container {
        padding: 24px 0 16px 0;
        margin-bottom: 25px;
        border-bottom: 1px solid #eaeaea;
    }
    
    .header-title {
        color: #000000;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 4px;
        letter-spacing: -0.8px;
    }
    
    .header-subtitle {
        color: #666666;
        font-size: 0.95rem;
        font-weight: 400;
        letter-spacing: -0.1px;
    }
    
    /* Premium Solid White Cards */
    .glass-card {
        background: #ffffff !important;
        border: 1px solid #eaeaea !important;
        border-radius: 8px !important;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    
    /* Corporate Styled Inputs */
    div.stTextInput > label, div.stTextArea > label {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    div.stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        transition: border-color 0.15s ease !important;
    }
    div.stTextInput input:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }
    
    /* --- STRICT MONOCHROMATIC WHITE SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #eaeaea !important;
    }
    
    /* Force all text elements, headers, and paragraph outputs inside the sidebar to be solid black */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] .sidebar-section-header {
        font-size: 0.75rem;
        font-weight: 800;
        color: #000000 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 20px 0 10px 0;
        border-bottom: 1px solid #eaeaea !important;
        padding-bottom: 4px;
    }
    
    /* Strict styling for metrics inside sidebar */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Strict styling for inputs inside sidebar */
    [data-testid="stSidebar"] div.stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebar"] div.stTextInput input:focus {
        border-color: #000000 !important;
    }
    
    /* Strict styling for alerts/callouts in sidebar */
    [data-testid="stSidebar"] div[data-testid="stAlert"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #eaeaea !important;
        border-radius: 6px !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] div[data-testid="stAlert"] p {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stAlert"] [data-testid="stNotificationIcon"] {
        color: #000000 !important;
    }

    /* Minimal Pipeline Stepper */
    .step-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 30px;
        padding: 0;
        background: transparent;
        border: none;
    }
    
    .step-box {
        flex: 1;
        text-align: center;
        padding: 10px 4px;
        margin: 0 4px;
        border-radius: 4px;
        font-size: 0.82rem;
        font-weight: 700;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .step-pending {
        background: #ffffff;
        color: #999999;
        border: 1px solid #eaeaea;
    }
    
    .step-active {
        background: #000000;
        color: #ffffff;
        border: 1px solid #000000;
    }
    
    .step-completed {
        background: #ffffff;
        color: #000000;
        border: 1px solid #000000;
    }
    
    .step-halted {
        background: #ffffff;
        color: #e11d48;
        border: 1px solid #e11d48;
    }

    /* Classy Monochromatic Buttons */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background-color: #fafafa !important;
        border-color: #888888 !important;
        color: #000000 !important;
    }
    
    /* Primary Block Action Button */
    div.stButton > button[type="primary"] {
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #000000 !important;
        box-shadow: none !important;
    }
    div.stButton > button[type="primary"]:hover {
        background: #222222 !important;
        border-color: #222222 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Minimal Light Card References */
    .paper-card {
        background: #ffffff;
        border: 1px solid #eaeaea;
        border-radius: 8px;
        padding: 16px;
        height: 100%;
        transition: border-color 0.15s ease;
    }
    .paper-card:hover {
        border-color: #000000;
    }
    
    .paper-title {
        font-weight: 700;
        font-size: 1rem;
        color: #000000;
        margin-bottom: 5px;
        letter-spacing: -0.2px;
    }
    
    .paper-authors {
        font-size: 0.85rem;
        color: #666666;
        margin-bottom: 8px;
    }
    
    .paper-badge {
        display: inline-block;
        background: #fafafa;
        color: #000000;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #eaeaea;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session States ---
if "pipeline_step" not in st.session_state:
    st.session_state.pipeline_step = "idle"  # idle, orchestrator, researcher, analyst, rag, operator_gate, coder, completed
if "query" not in st.session_state:
    st.session_state.query = ""
if "telemetry_logs" not in st.session_state:
    st.session_state.telemetry_logs = []
if "tokens_used" not in st.session_state:
    st.session_state.tokens_used = {"prompt": 0, "completion": 0, "cost": 0.0}
if "approval_granted" not in st.session_state:
    st.session_state.approval_granted = None

# --- Helper function to append telemetry logs ---
def add_log(agent, message, level="INFO", latency=None):
    timestamp = time.strftime("%H:%M:%S")
    lat_str = f" [{latency:.2f}s]" if latency else ""
    log_line = f"[{timestamp}] {level} [{agent}]{lat_str} — {message}"
    st.session_state.telemetry_logs.append(log_line)
    
    # Calculate mock token pricing based on pipeline execution steps
    prompt_tokens = random.randint(150, 450)
    completion_tokens = random.randint(100, 300)
    st.session_state.tokens_used["prompt"] += prompt_tokens
    st.session_state.tokens_used["completion"] += completion_tokens
    st.session_state.tokens_used["cost"] += (prompt_tokens * 0.0000015) + (completion_tokens * 0.0000045)

# --- Sidebar Layout: Workspace Settings & Observability ---
with st.sidebar:
    st.markdown('<div class="sidebar-section-header">🔌 Integration settings</div>', unsafe_allow_html=True)
    
    # Toggle between interactive sandbox and real connection
    app_mode = st.radio(
        "Application Mode:",
        ["✨ Interactive Sandbox Demo", "🔌 Live Vertex AI Agent Builder"],
        help="Interactive Sandbox runs beautiful simulations, while Live Integration connects to Vertex AI SDK."
    )
    
    # GCP Credentials (Visible only when in Live Integration Mode)
    if app_mode == "🔌 Live Vertex AI Agent Builder":
        st.info("💡 Ensure your environment has Application Default Credentials.")
        gcp_project = st.text_input("GCP Project ID:", placeholder="my-gcp-project-123")
        gcp_location = st.text_input("GCP Location ID:", value="us-central1")
        gcp_agent = st.text_input("Agent Builder Agent ID:", placeholder="0000-aaaa-1111-bbbb")
        gcp_session = st.text_input("Session ID:", value="researchforge-session-01")
        
        # Test widget embed option
        embed_widget = st.checkbox("Embed Chat Bubble Widget", value=False)
        if embed_widget and gcp_project and gcp_agent:
            import streamlit.components.v1 as components
            # Renders Dialogflow Messenger custom element
            df_html = f"""
            <script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
            <df-messenger
              location="{gcp_location}"
              project-id="{gcp_project}"
              agent-id="{gcp_agent}"
              language-code="en"
              chat-title="ResearchForge Copilot">
              <df-messenger-chat-bubble chat-title="ResearchForge Copilot"></df-messenger-chat-bubble>
            </df-messenger>
            <style>
              df-messenger {{
                --df-messenger-button-titlebar-color: #ffffff;
                --df-messenger-chat-background-color: #ffffff;
                --df-messenger-font-family: 'Inter';
                z-index: 99999;
              }}
            </style>
            """
            components.html(df_html, height=120)
    else:
        st.success("🎯 Sandbox Demo Mode enabled. Ready to run autonomous simulation graph.")
        
    st.markdown('<div class="sidebar-section-header">📊 Token statistics</div>', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("Total Tokens", f"{st.session_state.tokens_used['prompt'] + st.session_state.tokens_used['completion']:,}")
    with col_t2:
        st.metric("Pipeline Cost", f"${st.session_state.tokens_used['cost']:.4f}")
        
    st.markdown('<div class="sidebar-section-header">💾 Long-Term Memory (KB)</div>', unsafe_allow_html=True)
    if os.path.exists("knowledge_base.json"):
        with open("knowledge_base.json", "r") as f:
            try:
                db_data = json.load(f)
                st.write(f"Systems in Memory: `{len(db_data)}`")
                st.json(db_data[-1:])  # Show the last entry
            except:
                st.info("Memory database empty or corrupt.")
    else:
        st.info("Long-term database empty.")

# --- Main App Layout ---
st.markdown("""
<div class="header-container">
    <div class="header-title">⚡ ResearchForge AI</div>
    <div class="header-subtitle">Autonomous Research-to-Code Multi-Agent Engine grounded by Vertex AI & LangGraph</div>
</div>
""", unsafe_allow_html=True)

# Stepper Flow Tracker
def render_stepper():
    steps = [
        ("Orchestrator", ["orchestrator"]),
        ("Research", ["researcher"]),
        ("Analysis", ["analyst"]),
        ("RAG Grounding", ["rag"]),
        ("Human Approval", ["operator_gate"]),
        ("Code Generator", ["coder"]),
    ]
    
    current = st.session_state.pipeline_step
    
    stepper_html = '<div class="step-container">'
    for label, step_keys in steps:
        if current == "completed":
            css_class = "step-completed"
        elif current in step_keys:
            if current == "operator_gate":
                css_class = "step-halted"
            else:
                css_class = "step-active"
        elif any(st.session_state.get(f"done_{k}", False) for k in step_keys) or (
            steps.index((label, step_keys)) < next((i for i, (lbl, keys) in enumerate(steps) if current in keys), 99)
        ):
            css_class = "step-completed"
        else:
            css_class = "step-pending"
            
        stepper_html += f'<div class="step-box {css_class}">{label}</div>'
    stepper_html += '</div>'
    
    st.markdown(stepper_html, unsafe_allow_html=True)

render_stepper()

# Layout simplified to clean centered columns or collapsed side view
main_col, side_col = st.columns([3, 1])

with main_col:
    # 1. Setup Parameters
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💡 Request Code Copilot Orchestration")
        user_query = st.text_input(
            "What technical implementation query do you want researched & coded?",
            value="Build a scalable customer support RAG chatbot using latest papers from 2025.",
            placeholder="e.g. Build an asynchronous vector search system..."
        )
        
        trigger_btn = st.button(
            "🚀 Trigger Autonomous Agents",
            type="primary",
            disabled=(st.session_state.pipeline_step != "idle" and st.session_state.pipeline_step != "completed")
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. RUN PIPELINE EXECUTIONS
    if trigger_btn:
        st.session_state.query = user_query
        st.session_state.pipeline_step = "orchestrator"
        st.session_state.telemetry_logs = []
        st.session_state.approval_granted = None
        st.rerun()

    # Step 1: Root Orchestrator
    if st.session_state.pipeline_step == "orchestrator":
        with st.status("🧠 Root Orchestrator: Constructing DAG Graph...", expanded=True) as status:
            t_start = time.time()
            st.write("🔄 Parsing system requirements...")
            time.sleep(1.0)
            add_log("Orchestrator", "Received query. Generating task orchestration routing sequence.", latency=time.time()-t_start)
            
            st.write("🕸️ Mapping task flows: ResearchAgent ➔ AnalysisAgent ➔ Vector RAG ➔ CodeGenerator")
            time.sleep(1.0)
            add_log("Orchestrator", "Task mapping DAG complete. Initializing Research Agent API queries.", latency=time.time()-t_start)
            status.update(label="Orchestrator mapping completed!", state="complete")
        
        st.session_state.pipeline_step = "researcher"
        time.sleep(0.5)
        st.rerun()

    # Step 2: Research Agent
    elif st.session_state.pipeline_step == "researcher":
        with st.status("🔍 Research Agent: Fetching ArXiv academic papers...", expanded=True) as status:
            t_start = time.time()
            st.write("🌐 Querying ArXiv endpoint for latest 2024/2025 papers...")
            time.sleep(1.5)
            
            st.write("📄 Extracting metadata and parsing abstracts...")
            time.sleep(1.2)
            add_log("Researcher", "Queried ArXiv successfully. Retrieved 3 highly relevant 2024/2025 publications.", latency=time.time()-t_start)
            status.update(label="Research Agent complete!", state="complete")
            
        st.session_state.pipeline_step = "analyst"
        time.sleep(0.5)
        st.rerun()

    # Step 3: Analysis Agent
    elif st.session_state.pipeline_step == "analyst":
        with st.status("📊 Analysis Agent: Summarizing publication architectures...", expanded=True) as status:
            t_start = time.time()
            st.write("📝 Reviewing retrieved papers and cataloguing patterns...")
            time.sleep(1.2)
            
            st.write("⚖️ Comparing architectural tradeoffs (scalability, latency)...")
            time.sleep(1.0)
            add_log("Analyst", "Extracted trade-offs. Distilled optimal design: FastAPI backend, ChromaDB vector store, and Gemini 2.5 Flash on GCP Cloud Run.", latency=time.time()-t_start)
            status.update(label="Analysis Agent complete!", state="complete")
            
        st.session_state.pipeline_step = "rag"
        time.sleep(0.5)
        st.rerun()

    # Step 4: RAG Vector Grounding
    elif st.session_state.pipeline_step == "rag":
        with st.status("💾 RAG Pipeline: Vectorizing documents & indexing context...", expanded=True) as status:
            t_start = time.time()
            st.write("✂️ Splitting papers into semantic text chunks...")
            time.sleep(1.0)
            
            st.write("🧬 Generating vector embeddings via Google Gemini...")
            time.sleep(1.2)
            
            st.write("📦 Indexing vectors in local ChromaDB context block...")
            time.sleep(0.8)
            add_log("RAG Engine", "Document chunk embeddings stored. Injected 12 grounded context nodes into Coder prompt.", latency=time.time()-t_start)
            status.update(label="RAG grounding database indexing completed!", state="complete")
            
        st.session_state.pipeline_step = "operator_gate"
        time.sleep(0.5)
        st.rerun()

    # Step 5: Human Approval Gate
    elif st.session_state.pipeline_step == "operator_gate":
        st.warning("⚠️ **[Human Oversight Gate Triggered] Awaiting Manual Verification**")
        
        # Display the Proposed Design for Operator review
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid #000000; border-radius: 4px !important;">
            <h4 style="color: #000000; margin-top:0;">📋 Proposed System Blueprint</h4>
            <p style="color: #333333; font-size: 0.9rem; margin-bottom: 16px;">The agents have constructed a grounded architecture layout based on the retrieved 2025 papers. Review the proposed specifications below to authorize code generation.</p>
            <ul style="line-height: 1.8; font-size: 0.95rem; padding-left: 20px; color: #111111;">
                <li><strong>Gateway Backend:</strong> FastAPI Asynchronous Server Node</li>
                <li><strong>Vector Database:</strong> Local ChromaDB instance mapped inside memory container</li>
                <li><strong>LLM Core:</strong> Google Gemini 2.5 Flash</li>
                <li><strong>CI/CD Engine:</strong> GCP Cloud Build Container Registry Workflow</li>
                <li><strong>Hosting Target:</strong> Fully serverless GCP Cloud Run Service</li>
                <li><strong>Observability Span:</strong> OpenTelemetry logging mapped via Python standard routing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        app_col, den_col = st.columns(2)
        with app_col:
            if st.button("✅ Approve Blueprint & Generate Code", type="primary", use_container_width=True):
                st.session_state.approval_granted = True
                add_log("Human Gate", "Operator sign-off GRANTED. Advancing to Code Generation Node.", level="WARNING")
                st.session_state.pipeline_step = "coder"
                st.rerun()
        with den_col:
            if st.button("❌ Reject and Terminate Loop", use_container_width=True):
                st.session_state.approval_granted = False
                add_log("Human Gate", "Operator sign-off REJECTED. Aborting workflow execution.", level="ERROR")
                st.session_state.pipeline_step = "idle"
                st.rerun()

    # Step 6: Code Generation Agent
    elif st.session_state.pipeline_step == "coder":
        with st.status("💻 Code Agent: Engineering grounded system codebase...", expanded=True) as status:
            t_start = time.time()
            st.write("🧱 Assembling structured codebase layout...")
            time.sleep(1.5)
            
            st.write("🐍 Injecting FastAPI asynchronous handlers...")
            time.sleep(1.2)
            
            st.write("🐋 Generating production Docker & Cloud Build configurations...")
            time.sleep(1.0)
            
            # Save final data in memory base JSON for long term memory observability
            memory_record = {
                "query": st.session_state.query,
                "architecture": "FastAPI + ChromaDB + Cloud Run",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            if os.path.exists("knowledge_base.json"):
                try:
                    with open("knowledge_base.json", "r") as f:
                        records = json.load(f)
                except:
                    records = []
            else:
                records = []
            records.append(memory_record)
            with open("knowledge_base.json", "w") as f:
                json.dump(records, f, indent=2)
                
            add_log("Coder Agent", "System manifest output complete. Saved deployment signature in Knowledge Base memory.", latency=time.time()-t_start)
            status.update(label="Code Generation complete!", state="complete")
            
        st.session_state.pipeline_step = "completed"
        time.sleep(0.5)
        st.rerun()

    # Pipeline Complete: Render outputs
    if st.session_state.pipeline_step == "completed":
        st.success("🎉 Multi-Agent Copilot pipeline executed successfully! View the generated artifacts below.")
        
        # Display Research Papers
        st.markdown("### 📄 Grounded Paper Foundations (2024-2025)")
        
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            st.markdown("""
            <div class="paper-card">
                <div class="paper-title">1. Production RAG Scaling</div>
                <div class="paper-authors">Chen et al. — Jan 2025</div>
                <div class="paper-authors" style="margin-bottom: 12px; font-size: 0.88rem; line-height: 1.5; color: #555555;">Covers shard-based parallel vector index patterns for high-concurrency enterprise workloads.</div>
                <span class="paper-badge">Relevance: 94.2%</span>
            </div>
            """, unsafe_allow_html=True)
        with p_col2:
            st.markdown("""
            <div class="paper-card">
                <div class="paper-title">2. Multi-Agent Orchestrations</div>
                <div class="paper-authors">Smith & Patel — Feb 2025</div>
                <div class="paper-authors" style="margin-bottom: 12px; font-size: 0.88rem; line-height: 1.5; color: #555555;">Addresses strict workflow graph routing rules and human operator safety boundaries.</div>
                <span class="paper-badge">Relevance: 91.8%</span>
            </div>
            """, unsafe_allow_html=True)
        with p_col3:
            st.markdown("""
            <div class="paper-card">
                <div class="paper-title">3. Latency Optimization Patterns</div>
                <div class="paper-authors">Lopez et al. — Nov 2024</div>
                <div class="paper-authors" style="margin-bottom: 12px; font-size: 0.88rem; line-height: 1.5; color: #555555;">Analyzes semantic caching limits and dynamic chunk embedding compression strategies.</div>
                <span class="paper-badge">Relevance: 89.5%</span>
            </div>
            """, unsafe_allow_html=True)
                
        # Display Generated Code Workspace
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("### 🛠️ Generated System Workspace")
        tabs = st.tabs(["🚀 api.py", "🎨 streamlit_app.py", "🐋 Dockerfile", "☁️ cloudbuild.yaml"])
        
        with tabs[0]:
            st.code("""
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="ResearchForge RAG Engine API", version="1.0")
logger = logging.getLogger("api")

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: QueryRequest):
    \"\"\"
    Main grounded chat generation endpoint utilizing Gemini 2.5 Flash
    and RAG paper context retrieval.
    \"\"\"
    try:
        # 1. Mock context retrieval from indexed ChromaDB Vector Store
        context = (
            "Based on Chen et al. (2025), scaling production RAG pipelines "
            "requires a shard-based query framework with semantic cached route nodes."
        )
        
        # 2. Invoke Gemini Client
        client = genai.Client()
        prompt = f"Using this grounded paper context:\\n{context}\\n\\nAnswer: {request.query}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        return {
            "status": "success",
            "context_grounded": True,
            "response": response.text,
            "sources": ["arxiv:2501.04231"]
        }
    except Exception as e:
        logger.error(f"Generation failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy"}
            """, language="python")
            
        with tabs[1]:
            st.code("""
import streamlit as st
import requests

st.set_page_config(page_title="RAG Chatbot Service", page_icon="🤖")
st.title("🤖 Grounded Customer Chatbot")

user_input = st.text_input("Enter your question:")
if st.button("Send Query"):
    if user_input.strip():
        with st.spinner("Invoking FastAPI Grounding Engine..."):
            try:
                res = requests.post("http://localhost:8080/chat", json={"query": user_input})
                data = res.json()
                st.write("**Response:**")
                st.info(data.get("response"))
                st.caption(f"Sources utilized: {', '.join(data.get('sources', []))}")
            except Exception as e:
                st.error(f"Connection failure: {str(e)}")
            """, language="python")
            
        with tabs[2]:
            st.code("""
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
            """, language="dockerfile")
            
        with tabs[3]:
            st.code("""
steps:
  # 1. Build the container image in Google Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/researchforge-rag', '.']
    
  # 2. Push the container image to GCR
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/researchforge-rag']
    
  # 3. Deploy to managed Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'researchforge-rag'
      - '--image'
      - 'gcr.io/$PROJECT_ID/researchforge-rag'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
images:
  - 'gcr.io/$PROJECT_ID/researchforge-rag'
            """, language="yaml")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        if st.button("Reset Application & Run New Query"):
            st.session_state.pipeline_step = "idle"
            st.rerun()

with side_col:
    st.markdown("### 📊 Live Spans")
    with st.expander("🔍 Trace Logs", expanded=True):
        if st.session_state.telemetry_logs:
            log_text = "\n".join(st.session_state.telemetry_logs)
            st.code(log_text, language="bash")
        else:
            st.caption("Active trace logs stream in real-time when orchestration triggers.")