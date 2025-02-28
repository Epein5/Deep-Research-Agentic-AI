from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langchain.schema import Document
from agents.research_agent import ResearchAgent
from agents.drafter_agent import DrafterAgent

class ResearchState(TypedDict):
    """State object to track workflow progress."""
    query: str
    research_data: List[Document]
    draft_response: str
    final_response: str

class ResearchWorkflow:
    """Defines and manages the research workflow using LangGraph."""
    
    def __init__(self):
        self.graph = self._build_graph()
        self.research_agent = ResearchAgent()
        self.drafter_agent = DrafterAgent()

    def _research_node(self, state: ResearchState) -> dict:
        """Node to perform research."""
        research_data = self.research_agent.search(state["query"])
        return {"research_data": research_data}

    def _draft_node(self, state: ResearchState) -> dict:
        """Node to draft a response."""
        draft = self.drafter_agent.draft_response(state["query"], state["research_data"])
        print(f"Initial Response: {draft}")
        return {"draft_response": draft}

    def _refine_node(self, state: ResearchState) -> dict:
        """Node to refine the draft."""
        final = self.drafter_agent.refine_response(state["draft_response"])
        return {"final_response": final}

    def _build_graph(self) -> StateGraph:
        """Construct the workflow graph."""
        graph = StateGraph(ResearchState)
        graph.add_node("research", self._research_node)
        graph.add_node("draft", self._draft_node)
        graph.add_node("refine", self._refine_node)
        graph.add_edge("research", "draft")
        graph.add_edge("draft", "refine")
        graph.add_edge("refine", END)
        graph.set_entry_point("research")
        return graph.compile()

    def run(self, query: str) -> str:
        """Execute the workflow for a given query."""
        initial_state = {"query": query}
        result = self.graph.invoke(initial_state)
        return result["final_response"]