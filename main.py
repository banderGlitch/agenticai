from langgraph.graph import StateGraph, END, START
from typing import TypedDict, List, Dict, Any, Literal, Optional, Union, Annotated
import os
import sys
from src.agents.requirements_agent import gather_requirements
from src.agents.user_story_agent import generate_user_stories
from src.agents.design_agent import create_design_documents
from src.agents.code_agent import generate_code
from src.agents.test_agent import write_test_cases
from src.agents.qa_agent import qa_testing
from src.agents.deployment_agent import deploy_application
from src.utils.visualize import visualize_graph, export_graph_json, track_execution

# Define a simplified state schema
class SDLCState(TypedDict):
    project_name: str
    requirements: Optional[str]
    user_stories: Optional[str]
    design_documents: Optional[str]
    code: Optional[str]
    test_cases: Optional[str]
    qa_results: Optional[str]
    deployment_status: Optional[str]

def create_sdlc_graph():
    """
    Create a simplified LangGraph workflow for the SDLC process
    """
    # Initialize the graph
    workflow = StateGraph(SDLCState)
    
    # Add nodes for the main steps in the SDLC process
    workflow.add_node("gather_requirements", gather_requirements)
    workflow.add_node("generate_user_stories", generate_user_stories)
    workflow.add_node("create_design_documents", create_design_documents)
    workflow.add_node("generate_code", generate_code)
    workflow.add_node("write_test_cases", write_test_cases)
    workflow.add_node("qa_testing", qa_testing)
    workflow.add_node("deploy_application", deploy_application)
    
    # Define the entry point of the workflow
    workflow.add_edge(START, "gather_requirements")
    
    # Define a simple linear flow
    workflow.add_edge("gather_requirements", "generate_user_stories")
    workflow.add_edge("generate_user_stories", "create_design_documents")
    workflow.add_edge("create_design_documents", "generate_code")
    workflow.add_edge("generate_code", "write_test_cases")
    workflow.add_edge("write_test_cases", "qa_testing")
    workflow.add_edge("qa_testing", "deploy_application")
    workflow.add_edge("deploy_application", END)
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    # Print debug information
    print("Graph compiled successfully")
    print(f"Graph type: {type(compiled_graph)}")
    
    return compiled_graph

def main():
    """
    Main function to run the simplified SDLC workflow with LangGraph
    """
    print("Starting Simplified SDLC Workflow")
    
    # Initialize state
    project_name = input("Enter project name: ")
    initial_state = SDLCState(
        project_name=project_name,
        requirements=None,
        user_stories=None,
        design_documents=None,
        code=None,
        test_cases=None,
        qa_results=None,
        deployment_status=None
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