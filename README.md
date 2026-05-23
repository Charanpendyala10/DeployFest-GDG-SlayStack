# DeployFest-GDG-SlayStack
Hackathon for GDG Bangalore DeployFest
# 🔬 Deep-Evaluated Autonomous Research Orchestrator
An advanced, multi-agent academic-to-production research assistant built using the cutting-edge Google Agent Development Kit (ADK) and powered by Gemini 2.5 Flash. The platform accelerates deep engineering literature surveys, extracts production-ready architectures from academic sources (like ArXiv), runs structural validation guardrails, and deploys scalable FastAPI backend skeletons automatically.

🚀 Deployed Live on Google Cloud Run

🏗️ System Architecture & Workflow
The platform completely re-imagines multi-agent orchestration by moving away from unpredictable single-agent loops into an explicit, multi-phase state machine utilizing SequentialAgent execution tracks and strict Human-in-the-Loop (HITL) gates.

       [ User Objective ]
               │
               ▼
┌──────────────────────────────┐
│ Phase 1: Research & Analysis │ (research_and_analysis_pipeline)
│  ├─ research_agent           │ ───► Fetches grounded insights from ArXiv & Google
│  ├─ analysis_agent           │ ───► Compiles architectural metrics & ASCII trend charts
│  └─ human_oversight_agent    │ ───► Generates evaluation risk profile
└──────────────┬───────────────┘
               │
               ▼
     ⚠️ [HUMAN INTERRUPT GATE]  ◄─── System holds execution state for user approval
               │
          (Proceed)
               │
               ▼
┌──────────────────────────────┐
│  Phase 2: Implementation     │ (implementation_and_code_pipeline)
│  ├─ code_generation_agent    │ ───► Generates code implementation
│  └─ formatter_agent_2        │ ───► Compiles complete markdown report + APA citations
└──────────────┬───────────────┘
               │
               ▼
    [ Cloud Run Deployment ]
🤖 Core Agent Ecosystem
research_agent: Features an optimized arxiv client wrapper with built-in request pooling and an automatic 3-tier backoff retry policy to ingest implementation-focused literature without endpoint deprecation blocks.

analysis_agent: Parses text-heavy academic findings to emit architectural trend matrices and real-time analytical ASCII data histograms directly into the pipeline stream.

human_oversight_agent: Acts as a state-machine roadblock, calculating structural computing risks and deployment cost overheads to capture human guidance before expensive operational code changes take place.

code_generation_agent: A dedicated software engineering agent executing clean, modular, production-ready Python files equipped with logging and observability hooks.

formatter_agent_2: Normalizes all combined agent logs, system blueprints, and scraped metadata into comprehensive APA-formatted academic report packets.

🛠️ Features
Google ADK Native Architecture: Fully written utilizing Google Cloud's latest agent workspace standard framework, steering clear of legacy prompt-chaining hacks.

Model-to-Context Grounding Layer: Leverages an integrated Model Context Protocol (MCP) via MCPToolset with auto-managed google.auth bearer handshakes to connect live data pools securely.

Deterministic Execution Chains: Organizes multi-agent dependencies using native SequentialAgent boundaries to completely block race-conditions, loop-skips, or multi-agent context hallucinations.

Deep Observability Pipeline: Integrated telemetry framework mirroring structural OpenTelemetry span processor flows to print tool latencies and state shifts live into the stdout execution terminal.


☁️ Google Cloud Run Deployment
This platform is containerized and deployed into a highly available, autoscale environment using Google Cloud Run, pulling service access safely through Cloud IAM.


# Deploy to Cloud Run with unauthenticated access cleared for the hackathon panel
source .env

adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=europe-west2 \
  --service_name=research-assistant \
  --with_ui \
  .

gcloud run services update research-assistant \
  --region=europe-west2 \
  --update-labels=dev-tutorial=codelab-adk \
  --set-env-vars="MODEL=$MODEL,MCP_SERVER_URL=$MCP_SERVER_URL,GOOGLE_CLOUD_LOCATION=global"'

🔬 Evaluation Hackathon Criteria Targets Met
Agents / Freestyle Track: Implements real-world multi-agent cooperative problem-solving patterns.

Deep Observability & Telemetry: Emits structural terminal log data and handles custom validation guardrails natively inside the orchestrator flow loops.

Human-In-The-Loop: Zero auto-progression to code generation without manual checkpoint validation responses from the operator.

Google Cloud Ecosystem Integration: Uses Gemini models natively via Google ADK, authenticates through google.auth, and leverages Cloud Run for serverless auto-scaling microservices.