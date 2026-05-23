import os
import sys
import logging
from dotenv import load_dotenv


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool


import google.auth
import google.auth.transport.requests
import google.oauth2.id_token
import arxiv
import time
# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

  # Greet user and save their prompt

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}

  # Configuring the MCP Tool to connect to the Zoo MCP server

mcp_server_url = os.getenv("MCP_SERVER_URL")
if not mcp_server_url:
    raise ValueError("The environment variable MCP_SERVER_URL is not set.")

def get_id_token():
    """Get an ID token to authenticate with the MCP server."""
    target_url = os.getenv("MCP_SERVER_URL")
    audience = target_url.split('/mcp/')[0]
    request = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(request, audience)
    return id_token

"""
## Use this code if you are using the public MCP Server and comment out the code below defining mcp_tools
mcp_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url
    )
)
"""

mcp_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url,
        headers={
            "Authorization": f"Bearer {get_id_token()}",
        },
    ),
)


# --- ArXiv API Tool ---
def search_arxiv(query: str, max_results: int = 5) -> str:
    """
    Searches ArXiv for research papers matching the query.
    Includes retry logic and uses the updated Client API to avoid deprecation warnings.
    
    Args:
        query: Search query for papers
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Formatted string with paper details
    """
    client = arxiv.Client()
    
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    results = []
    try:
        # Use client.results() instead of search.results() to fix deprecation warning
        # and add retry logic for robustness
        for attempt in range(3):
            try:
                # Convert generator to list to ensure we actually fetch data
                found_papers = list(client.results(search))
                break
            except Exception as e:
                if attempt == 2: # Last attempt
                    raise e
                time.sleep(1) # Wait 1s before retry
        
        for paper in found_papers:
            result = {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "summary": paper.summary[:300] + "..." if len(paper.summary) > 300 else paper.summary,
                "published": paper.published.strftime("%Y-%m-%d"),
                "url": paper.entry_id,
                "pdf_url": paper.pdf_url
            }
            results.append(result)
            
        if not results:
            return f"No papers found for query: {query}"
            
        # Format results
        formatted = f"Found {len(results)} papers for '{query}':\n\n"
        for i, paper in enumerate(results, 1):
            authors = ", ".join(paper["authors"][:3])
            if len(paper["authors"]) > 3:
                authors += " et al."
            formatted += f"{i}. **{paper['title']}**\n"
            formatted += f"   Authors: {authors}\n"
            formatted += f"   Published: {paper['published']}\n"
            formatted += f"   URL: {paper['url']}\n"
            formatted += f"   Summary: {paper['summary']}\n\n"
            
        cloud_logging_client.info(f"ArXiv search completed: {len(results)} results for '{query}'")
        return formatted
        
    except Exception as e:
        error_msg = f"ArXiv search failed: {str(e)}"
        cloud_logging_client.error(error_msg)
        return f"Error searching ArXiv: {str(e)}"

print("✅ ArXiv search tool defined (updated with Client API and retries).")

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context

research_agent_google_search_agent = LlmAgent(
  name='Research_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
research_agent_url_context_agent = LlmAgent(
  name='Research_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
research_agent = LlmAgent(
  name='research_agent',
  model='gemini-2.5-flash',
  description=(
      'Responsible for searching and retrieving the latest research papers from ArXiv and related academic sources. Focuses on implementation-oriented and production-ready AI research.'
  ),
  sub_agents=[],
  instruction='You are an expert AI Research Agent.\n\nYour responsibilities:\n1. Search for relevant research papers using available tools.\n2. Focus on recent papers from 2023-2026.\n3. Prioritize implementation-focused research.\n4. Extract important technical details.\n\nFor each paper extract:\n- title\n- authors\n- publication year\n- abstract summary\n- methodology\n- benchmarks\n- architecture insights\n- GitHub repositories if available\n- paper URL\n\nFocus Areas:\n- multi-agent systems\n- RAG pipelines\n- observability\n- autonomous AI systems\n- deployment architecture\n- scalable infrastructure\n\nIMPORTANT:\n- Prefer practical engineering papers.\n- Avoid purely theoretical research.\n- Focus on deployment-ready approaches.\n- Return structured markdown output.',
  tools=[
    agent_tool.AgentTool(agent=research_agent_google_search_agent),
    agent_tool.AgentTool(agent=research_agent_url_context_agent),
    search_arxiv
  ],
)
analysis_agent_google_search_agent = LlmAgent(
  name='Analysis_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
analysis_agent_url_context_agent = LlmAgent(
  name='Analysis_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
analysis_agent = LlmAgent(
  name='analysis_agent',
  model='gemini-2.5-flash',
  description=(
      'Analyzes research findings, compares implementation approaches, identifies architecture trends, and recommends scalable engineering solutions.'
  ),
  sub_agents=[],
  instruction='You are an AI Research Analyst.\n\nYour responsibilities:\n1. Analyze research papers and grounded context.\n2. Compare methodologies and architectures.\n3. Identify engineering trends.\n4. Recommend scalable implementation approaches.\n5. Evaluate tradeoffs across solutions.\n6. Generate publication trend analysis.\n\nYou should analyze:\n- scalability\n- deployment feasibility\n- observability support\n- infrastructure complexity\n- cost efficiency\n- production readiness\n\nGenerate:\n- architecture comparisons\n- implementation recommendations\n- ASCII trend charts\n- engineering summaries\n\nASCII Example:\n2026: **** (4 papers)\n2025: ****** (6 papers)\n2024: *** (3 papers)\n\nIMPORTANT:\n- Focus on practical implementation.\n- Prefer cloud-native scalable systems.\n- Keep insights concise and actionable.',
  tools=[
    agent_tool.AgentTool(agent=analysis_agent_google_search_agent),
    agent_tool.AgentTool(agent=analysis_agent_url_context_agent)
  ],
)
planner_agent_google_search_agent = LlmAgent(
  name='Planner_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
planner_agent_url_context_agent = LlmAgent(
  name='Planner_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
planner_agent = LlmAgent(
  name='planner_agent',
  model='gemini-2.5-flash',
  description=(
      '\nDesigns implementation architecture, defines workflows, recommends infrastructure, and creates execution plans optimized for hackathon MVP development.'
  ),
  sub_agents=[],
  instruction='You are a Senior AI Solutions Architect.\n\nYour responsibilities:\n1. Create implementation architecture plans.\n2. Design scalable workflows.\n3. Recommend technology stacks.\n4. Define deployment architecture.\n5. Create execution timelines.\n6. Generate folder structures and APIs.\n\nPreferred Stack:\n- FastAPI\n- LangGraph\n- ChromaDB\n- Streamlit\n- Cloud Run\n- Gemini\n\nYou should generate:\n- system architecture\n- execution workflow\n- deployment plan\n- API structure\n- folder structure\n- cloud architecture\n\nIMPORTANT:\n- Prioritize simplicity and speed.\n- Optimize for hackathon MVP delivery.\n- Avoid overengineering.\n- Prefer production-ready patterns.\n',
  tools=[
    agent_tool.AgentTool(agent=planner_agent_google_search_agent),
    agent_tool.AgentTool(agent=planner_agent_url_context_agent)
  ],
)
code_generation_agent_google_search_agent = LlmAgent(
  name='Code_Generation_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
code_generation_agent_url_context_agent = LlmAgent(
  name='Code_Generation_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
code_generation_agent = LlmAgent(
  name='code_generation_agent',
  model='gemini-2.5-flash',
  description=(
      'Generates implementation-ready code, backend services, frontend scaffolding, deployment configurations, and infrastructure templates.'
  ),
  sub_agents=[],
  instruction='You are an Expert AI Software Engineer.\n\nYour responsibilities:\n1. Generate clean modular code.\n2. Create FastAPI backend services.\n3. Generate Streamlit frontend scaffolding.\n4. Create LangGraph workflows.\n5. Generate Docker deployment files.\n6. Add observability hooks and logging.\n\nGenerate:\n- Python APIs\n- starter templates\n- Dockerfiles\n- requirements.txt\n- environment setup\n- logging integration\n- deployment scripts\n\nCoding Principles:\n- readability\n- modularity\n- scalability\n- maintainability\n- minimal complexity\n\nIMPORTANT:\n- Generate concise working code.\n- Optimize for fast implementation.\n- Avoid unnecessary abstraction.\n- Include comments where useful.',
  tools=[
    agent_tool.AgentTool(agent=code_generation_agent_google_search_agent),
    agent_tool.AgentTool(agent=code_generation_agent_url_context_agent)
  ],
)

formatter_agent_google_search_agent = LlmAgent(
  name='Formatter_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
formatter_agent_url_context_agent = LlmAgent(
  name='Formatter_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
formatter_agent_2 = LlmAgent(
  name='formatter_agent_2',
  model='gemini-2.5-flash',
  description=(
      'Formats research findings into clean professional reports and converts paper metadata into academic citation formats.'
  ),
  sub_agents=[],
  instruction='You are an Academic Citation and Reporting Expert.\n\nYour responsibilities:\n1. Format research papers into APA citations.\n2. Create professional markdown reports.\n3. Organize outputs clearly.\n4. Improve readability and presentation quality.\n\nReports should include:\n- research summary\n- architecture recommendations\n- implementation plan\n- trend analysis\n- citations\n- deployment recommendations\n\nCitation Format:\nAuthors (Year). Title. Retrieved from URL\n\nIMPORTANT:\n- Maintain professional formatting.\n- Keep reports concise and readable.\n- Ensure citations are accurate.\n- Structure outputs using markdown headings and lists.',
  tools=[
    agent_tool.AgentTool(agent=formatter_agent_google_search_agent),
    agent_tool.AgentTool(agent=formatter_agent_url_context_agent)
  ],
)
orchestrator_agent_google_search_agent = LlmAgent(
  name='Orchestrator_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
orchestrator_agent_url_context_agent = LlmAgent(
  name='Orchestrator_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
human_oversight_agent_google_search_agent = LlmAgent(
  name='Human_Oversight_Agent_google_search_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
human_oversight_agent_url_context_agent = LlmAgent(
  name='Human_Oversight_Agent_url_context_agent',
  model='gemini-2.5-flash',
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
# --- 1. Repurpose Human Oversight Agent for the Mid-Stage Gate ---
# This agent will act as the gatekeeper right after Step 3 (Analysis)
human_oversight_agent = LlmAgent(
    name='human_oversight_agent',
    model='gemini-2.5-flash',
    description=(
        'Halts the autonomous pipeline after research analysis to present findings and explicitly request user validation/modifications before proceeding to planning and code generation.'
    ),
    sub_agents=[],
    instruction=(
        'You are the Validation Gatekeeper.\n\n'
        'Your responsibilities:\n'
        '1. Receive and review the Research Findings and Technical Analysis.\n'
        '2. Present a concise engineering summary of the chosen approaches (e.g., Multimodal Fusion, MST-AI skin tone correction).\n'
        '3. EXPLICITLY ask the user for feedback, additions, or a confirmation to proceed.\n'
        '4. Stop execution here and output the review request. Do not generate code or architecture plans yet.\n\n'
        'Output Format Example:\n'
        '### 📊 Research Analysis Review\n'
        '[Provide short summary of findings and tradeoffs here]\n\n'
        '**Ready for Implementation?** Please reply with your adjustments or type "Proceed" to trigger the architecture design and code generation.'
    ),
    tools=[
        agent_tool.AgentTool(agent=human_oversight_agent_google_search_agent),
        agent_tool.AgentTool(agent=human_oversight_agent_url_context_agent)
    ],
)

# --- 2. Create Explicit Multi-Agent Pipelines ---
# To avoid the orchestration dropping the ball, we group the lifecycle cleanly.
from google.adk.agents import SequentialAgent

# Phase 1 Pipeline: Gathers and Analyzes information, then stops for your input.
research_and_analysis_pipeline = SequentialAgent(
    name="research_and_analysis_pipeline",
    description="Executes the research, analysis, and presents the human gating mechanism.",
    sub_agents=[research_agent, analysis_agent, human_oversight_agent]
)

# Phase 2 Pipeline: Handles the heavy lifting of architecture and coding once you say go.
implementation_and_code_pipeline = SequentialAgent(
    name="implementation_and_code_pipeline",
    description="Takes the approved insights and generates system architecture and modular code.",
    sub_agents=[planner_agent, code_generation_agent, formatter_agent_2]
)


# --- 3. Update the Master Orchestrator (root_agent) ---
root_agent = LlmAgent(
    name='Orchestrator_Agent',
    model='gemini-2.5-flash',
    description=(
        'The central coordinator managing the execution state. It switches between the Analysis Phase and Implementation Phase based on user input.'
    ),
    # Register both high-level pipelines as sub-agents
    sub_agents=[research_and_analysis_pipeline, implementation_and_code_pipeline],
    instruction=(
        'You are the Lead AI Research and Implementation Coordinator.\n\n'
        'Your Core Operational Logic:\n'
        '- IF the user is initiating a new request (e.g., "I want to implement an AI solution..."): '
        'Delegate entirely to the `research_and_analysis_pipeline`. Let it run completely through research and analysis, and stop at the confirmation prompt.\n\n'
        '- IF the user provides feedback or says "Proceed" to an existing research summary: '
        'Forward the accumulated research context along with the user\'s feedback to the `implementation_and_code_pipeline` to generate the system architecture blueprints, production-ready code modules, and final academic citations.\n\n'
        'IMPORTANT:\n'
        '- Maintain execution history in the state.\n'
        '- Do not let the pipeline automatically jump into coding until Phase 1 has outputted its summary and the user has interacted.'
    ),
    tools=[
        agent_tool.AgentTool(agent=orchestrator_agent_google_search_agent),
        agent_tool.AgentTool(agent=orchestrator_agent_url_context_agent)
    ],
)