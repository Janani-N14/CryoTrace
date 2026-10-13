import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# ==========================================
# 1. SETUP & PATH RESOLUTION
# ==========================================
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parents[0]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agent_tools import query_telemetry_db, fetch_corridor_conditions, search_compliance_sop

load_dotenv(project_root / ".env")

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ==========================================
# 2. FACTORY INITIALIZATION: AGENT REASONER LLM
# ==========================================

fde_tools = [query_telemetry_db, fetch_corridor_conditions, search_compliance_sop]

def build_llm(llm_setting: str = None, api_key: str = None):
    setting = (llm_setting or os.getenv("Agent_llm", "GROQ")).strip().upper()
    
    if setting == "OPENAI":
        key = api_key or os.getenv("OPENAI_API_KEY")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o", temperature=0, api_key=key)

    elif setting == "DEEPSEEK":
        key = api_key or os.getenv("DEEPSEEK_API_KEY")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="deepseek-v4-flash",
            temperature=0,
            openai_api_key=key,
            base_url="https://api.deepseek.com",
            max_tokens=2048
        )

    elif setting == "GROQ":
        key = api_key or os.getenv("GROQ_API_KEY")
        groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=groq_model,
            temperature=0,
            api_key=key,
            base_url="https://api.groq.com/openai/v1",
            max_tokens=2048
        )

    else:
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(model="qwen2.5:7b", temperature=0, num_predict=1024)

def create_agent(llm_setting: str = None, api_key: str = None):
    active_llm = build_llm(llm_setting, api_key)
    bound_tools = active_llm.bind_tools(fde_tools)

    def reasoning_node(state: AgentState):
        response = bound_tools.invoke(state["messages"])
        return {"messages": [response]}

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("reasoner", reasoning_node)
    graph_builder.add_node("tools", ToolNode(fde_tools))
    graph_builder.add_edge(START, "reasoner")
    graph_builder.add_conditional_edges("reasoner", tools_condition)
    graph_builder.add_edge("tools", "reasoner")
    return graph_builder.compile(checkpointer=MemorySaver())

AGENT_LLM_SETTING = os.getenv("Agent_llm", "GROQ").strip().upper()
fde_agent = create_agent(AGENT_LLM_SETTING)

# ==========================================
# 4. CHAT LOOP TESTING PANEL
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("[READY] FDE Supply Chain Orchestrator State Machine Online")
    print(f"   Configured Execution: [LLM: {AGENT_LLM_SETTING}] -> [Embeddings: {os.getenv('Embeddings_model', 'LOCAL')}]")
    print("="*55 + "\n")
    
    # Load the business-structured system prompt from the external file
    prompt_path = project_root / "src" / "prompts" / "system_prompt.txt"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instructions = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {prompt_path}")
        system_instructions = "You are a helpful AI assistant." # Basic fallback

    system_prompt = SystemMessage(content=system_instructions)
    
    thread_config = {"configurable": {"thread_id": "production_test_1"}}
    fde_agent.invoke({"messages": [system_prompt]}, config=thread_config)
    
    while True:
        user_input = input("\nDispatcher > ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        events = fde_agent.stream({"messages": [("user", user_input)]}, config=thread_config, stream_mode="updates")
        for event in events:
            for node_name, node_state in event.items():
                if node_name == "tools":
                    print("   [System] 🔄 Retrieving external data elements via ToolNode...")
                elif node_name == "reasoner":
                    latest_msg = node_state["messages"][-1]
                    if latest_msg.content:
                        print(f"\n🤖 FDE Agent:\n{latest_msg.content}")