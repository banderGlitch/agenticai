import os
import sys
from main import create_sdlc_graph, SDLCState
from src.utils.visualize import visualize_graph, export_graph_json, track_execution

def run_demo():
    """
    Run a demo of the SDLC workflow with sample inputs
    """
    print("Running SDLC Agents Demo with LangGraph")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Initialize state with sample project
    initial_state = SDLCState(
        project_name="Demo Task Manager",
        requirements=None,
        user_stories=None,
        design_documents=None,
        code=None,
        test_cases=None,
        deployment_status=None,
        monitoring_data=None,
        # Pre-populate raw requirements to skip user input
        raw_requirements_input="""
        I need a simple task management application with the following features:
        - User authentication (login/register)
        - Create, read, update, delete tasks
        - Assign due dates to tasks
        - Mark tasks as complete
        - Filter tasks by status and due date
        - Simple dashboard showing task statistics
        - Mobile-responsive design
        """
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
    print("\nStarting workflow execution...")
    print("Note: This demo will pause at review steps. Enter 'Approved' to continue.")
    
    execution_history = {}
    try:
        for step, state in sdlc_graph.stream(initial_state):
            if step.name != "__end__":
                print(f"\n--- Completed Step: {step.name} ---")
                # Store state history for tracking
                execution_history[step.name] = dict(state)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during workflow execution: {e}")
    
    # Save execution history
    try:
        track_execution(execution_history)
    except Exception as e:
        print(f"Warning: Could not save execution history: {e}")
    
    print("\nSDLC Demo Completed!")
    print("Check the 'output' directory for generated artifacts and visualizations.")

if __name__ == "__main__":
    run_demo() 