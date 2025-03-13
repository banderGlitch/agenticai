from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Literal, Optional, Union, Annotated
import os
import sys
from src.agents.requirements_agent import gather_requirements
from src.agents.user_story_agent import generate_user_stories
from src.agents.review_agent import review_user_stories, user_approve_review
from src.agents.design_agent import create_design_documents, review_design
from src.agents.code_agent import generate_code, review_code, fix_code_after_review
from src.agents.security_agent import security_review, fix_code_after_security
from src.agents.test_agent import write_test_cases, review_test_cases, fix_test_cases
from src.agents.qa_agent import qa_testing, fix_code_after_qa
from src.agents.deployment_agent import deploy_application
from src.agents.monitoring_agent import monitor_application
from src.agents.maintenance_agent import maintain_application
from src.utils.visualize import visualize_graph, export_graph_json, track_execution

# Define the state schema
class SDLCState(TypedDict):
    project_name: str
    requirements: Optional[Union[Dict[str, Any], str]]
    raw_requirements_input: Optional[str]
    user_stories: Optional[str]
    review_feedback: Optional[str]
    review_status: Optional[str]
    design_documents: Optional[str]
    design_review_feedback: Optional[str]
    design_review_status: Optional[str]
    code: Optional[str]
    code_review_feedback: Optional[str]
    code_review_status: Optional[str]
    fixed_code: Optional[str]
    security_review_feedback: Optional[str]
    security_review_status: Optional[str]
    security_fixed_code: Optional[str]
    test_cases: Optional[str]
    test_review_feedback: Optional[str]
    test_review_status: Optional[str]
    fixed_test_cases: Optional[str]
    qa_results: Optional[str]
    qa_status: Optional[str]
    qa_fixed_code: Optional[str]
    deployment_plan: Optional[str]
    deployment_status: Optional[str]
    monitoring_plan: Optional[str]
    monitoring_data: Optional[Dict[str, Any]]
    maintenance_plan: Optional[str]

def create_sdlc_graph():
    """
    Create the LangGraph workflow for the SDLC process
    """
    # Initialize the graph
    workflow = StateGraph(SDLCState)
    
    # Add nodes for each step in the SDLC process
    workflow.add_node("gather_requirements", gather_requirements)
    workflow.add_node("generate_user_stories", generate_user_stories)
    workflow.add_node("review_user_stories", review_user_stories)
    workflow.add_node("revise_user_stories", lambda state: generate_user_stories(state, revision=True))
    workflow.add_node("create_design_documents", create_design_documents)
    workflow.add_node("review_design", review_design)
    workflow.add_node("generate_code", generate_code)
    workflow.add_node("review_code", review_code)
    workflow.add_node("fix_code_after_review", fix_code_after_review)
    workflow.add_node("security_review", security_review)
    workflow.add_node("fix_code_after_security", fix_code_after_security)
    workflow.add_node("write_test_cases", write_test_cases)
    workflow.add_node("review_test_cases", review_test_cases)
    workflow.add_node("fix_test_cases", fix_test_cases)
    workflow.add_node("qa_testing", qa_testing)
    workflow.add_node("fix_code_after_qa", fix_code_after_qa)
    workflow.add_node("deploy_application", deploy_application)
    workflow.add_node("monitor_application", monitor_application)
    workflow.add_node("maintain_application", maintain_application)
    
    # Define the edges (workflow transitions)
    # Requirements -> User Stories
    workflow.add_edge("gather_requirements", "generate_user_stories")
    
    # User Stories -> Review
    workflow.add_edge("generate_user_stories", "review_user_stories")
    workflow.add_edge("revise_user_stories", "review_user_stories")
    
    # Review -> Design or Revise
    workflow.add_conditional_edges(
        "review_user_stories",
        lambda state: "revise" if state["review_status"] == "Needs Revision" else "proceed",
        {
            "revise": "revise_user_stories",
            "proceed": "create_design_documents"
        }
    )
    
    # Design -> Design Review
    workflow.add_edge("create_design_documents", "review_design")
    
    # Design Review -> Code Generation
    workflow.add_conditional_edges(
        "review_design",
        lambda state: "proceed" if state["design_review_status"] == "Approved" else "revise",
        {
            "proceed": "generate_code",
            "revise": "create_design_documents"  # Loop back to revise design
        }
    )
    
    # Code Generation -> Code Review
    workflow.add_edge("generate_code", "review_code")
    
    # Code Review -> Security Review or Fix Code
    workflow.add_conditional_edges(
        "review_code",
        lambda state: "fix" if state.get("code_review_status") == "Needs Revision" else "proceed",
        {
            "fix": "fix_code_after_review",
            "proceed": "security_review"
        }
    )
    
    # Fix Code -> Security Review
    workflow.add_edge("fix_code_after_review", "security_review")
    
    # Security Review -> Write Tests or Fix Security Issues
    workflow.add_conditional_edges(
        "security_review",
        lambda state: "fix" if state.get("security_review_status") == "Needs Security Fixes" else "proceed",
        {
            "fix": "fix_code_after_security",
            "proceed": "write_test_cases"
        }
    )
    
    # Fix Security Issues -> Write Tests
    workflow.add_edge("fix_code_after_security", "write_test_cases")
    
    # Write Tests -> Test Review
    workflow.add_edge("write_test_cases", "review_test_cases")
    
    # Test Review -> QA Testing or Fix Tests
    workflow.add_conditional_edges(
        "review_test_cases",
        lambda state: "fix" if state.get("test_review_status") == "Needs Revision" else "proceed",
        {
            "fix": "fix_test_cases",
            "proceed": "qa_testing"
        }
    )
    
    # Fix Tests -> QA Testing
    workflow.add_edge("fix_test_cases", "qa_testing")
    
    # QA Testing -> Deployment or Fix Code
    workflow.add_conditional_edges(
        "qa_testing",
        lambda state: "fix" if state.get("qa_status") == "Failed" else "proceed",
        {
            "fix": "fix_code_after_qa",
            "proceed": "deploy_application"
        }
    )
    
    # Fix Code after QA -> QA Testing (retest)
    workflow.add_edge("fix_code_after_qa", "qa_testing")
    
    # Deployment -> Monitoring
    workflow.add_edge("deploy_application", "monitor_application")
    
    # Monitoring -> Maintenance
    workflow.add_edge("monitor_application", "maintain_application")
    
    # Maintenance -> End
    workflow.add_edge("maintain_application", END)
    
    return workflow.compile()

def main():
    """
    Main function to run the SDLC workflow with LangGraph
    """
    print("Starting SDLC Agents Workflow with LangGraph")
    
    # Initialize state
    project_name = input("Enter project name: ")
    initial_state = SDLCState(
        project_name=project_name,
        requirements=None,
        user_stories=None,
        design_documents=None,
        code=None,
        test_cases=None,
        deployment_status=None,
        monitoring_data=None
    )
    
    # Create the workflow graph
    sdlc_graph = create_sdlc_graph()
    
    # Visualize the graph
    try:
        print("Generating workflow visualization...")
        visualize_graph(sdlc_graph)
        export_graph_json(sdlc_graph)
    except Exception as e:
        print(f"Warning: Could not generate visualization: {e}")
    
    # Execute the workflow
    execution_history = {}
    for step, state in sdlc_graph.stream(initial_state):
        if step.name != "__end__":
            print(f"\n--- Completed Step: {step.name} ---")
            # Store state history for tracking
            execution_history[step.name] = dict(state)
    
    # Save execution history
    try:
        track_execution(execution_history)
    except Exception as e:
        print(f"Warning: Could not save execution history: {e}")
    
    print("\nSDLC Workflow Completed!")
    return state

if __name__ == "__main__":
    main() 