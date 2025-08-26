from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langchain.schema import Document
from agents.research_agent import ResearchAgent
from agents.drafter_agent import DrafterAgent
import logging

logger = logging.getLogger(__name__)

class ResearchState(TypedDict):
    """State object to track workflow progress."""
    query: str
    research_data: List[Document]
    draft_response: str
    final_response: str
    sources: List[dict]
    error: Optional[str]
    metadata: dict

class ResearchWorkflow:
    """Defines and manages the research workflow using LangGraph."""
    
    def __init__(self):
        self.graph = self._build_graph()
        self.research_agent = ResearchAgent()
        self.drafter_agent = DrafterAgent()

    def _research_node(self, state: ResearchState) -> dict:
        """Node to perform research."""
        try:
            logger.info(f"Starting research for query: {state['query']}")
            research_data = self.research_agent.search(state["query"])
            
            if not research_data:
                logger.warning("No research data found")
                return {
                    "research_data": [],
                    "error": "No relevant research data found",
                    "metadata": {"research_status": "no_results"}
                }
            
            logger.info(f"Found {len(research_data)} research documents")
            return {
                "research_data": research_data,
                "metadata": {"research_status": "success", "num_documents": len(research_data)}
            }
        except Exception as e:
            logger.error(f"Research node failed: {str(e)}")
            return {
                "research_data": [],
                "error": f"Research failed: {str(e)}",
                "metadata": {"research_status": "failed"}
            }

    def _draft_node(self, state: ResearchState) -> dict:
        """Node to draft a response."""
        try:
            if state.get("error") or not state.get("research_data"):
                fallback_response = "I apologize, but I couldn't find relevant information to answer your question. Please try rephrasing your query or check back later."
                return {
                    "draft_response": fallback_response,
                    "sources": [],
                    "metadata": {**state.get("metadata", {}), "draft_status": "no_data"}
                }
            
            logger.info("Generating draft response...")
            draft = self.drafter_agent.draft_response(state["query"], state["research_data"])
            
            # Extract sources from research data
            sources = self.drafter_agent.get_sources_from_research_data(state["research_data"])
            
            # Check if draft contains API error messages
            if "API quota exceeded" in draft or "unable to generate" in draft.lower():
                logger.warning("Draft generation hit API limits")
                return {
                    "draft_response": draft,
                    "sources": sources,
                    "error": "API quota exceeded",
                    "metadata": {**state.get("metadata", {}), "draft_status": "api_limited"}
                }
            
            logger.info("Draft response generated successfully")
            return {
                "draft_response": draft,
                "sources": sources,
                "metadata": {**state.get("metadata", {}), "draft_status": "success"}
            }
        except Exception as e:
            logger.error(f"Draft node failed: {str(e)}")
            fallback_response = f"I encountered an error while generating the response: {str(e)}"
            return {
                "draft_response": fallback_response,
                "sources": [],
                "error": f"Draft generation failed: {str(e)}",
                "metadata": {**state.get("metadata", {}), "draft_status": "failed"}
            }

    def _refine_node(self, state: ResearchState) -> dict:
        """Node to refine the draft."""
        try:
            # Skip refinement if there's an error or API is limited
            if state.get("error") and "quota" in state.get("error", "").lower():
                logger.info("Skipping refinement due to API quota limits")
                return {
                    "final_response": state.get("draft_response", "An error occurred."),
                    "metadata": {**state.get("metadata", {}), "refine_status": "skipped"}
                }
            
            logger.info("Refining response...")
            final = self.drafter_agent.refine_response(state["draft_response"])
            
            logger.info("Response refinement completed successfully")
            return {
                "final_response": final,
                "sources": state.get("sources", []),
                "metadata": {**state.get("metadata", {}), "refine_status": "success"}
            }
        except Exception as e:
            logger.error(f"Refine node failed: {str(e)}")
            # Return the draft if refinement fails
            return {
                "final_response": state.get("draft_response", "An error occurred during refinement."),
                "sources": state.get("sources", []),
                "metadata": {**state.get("metadata", {}), "refine_status": "failed"}
            }

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

    def run(self, query: str) -> dict:
        """Execute the workflow for a given query and return detailed results."""
        initial_state = {
            "query": query,
            "research_data": [],
            "draft_response": "",
            "final_response": "",
            "sources": [],
            "error": None,
            "metadata": {}
        }
        
        try:
            result = self.graph.invoke(initial_state)
            return {
                "response": result["final_response"],
                "sources": result.get("sources", []),
                "metadata": result.get("metadata", {}),
                "error": result.get("error"),
                "num_sources": len(result.get("research_data", [])),
                "success": not result.get("error")
            }
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "response": f"Workflow failed: {str(e)}",
                "metadata": {"workflow_status": "failed"},
                "error": str(e),
                "num_sources": 0,
                "success": False
            }