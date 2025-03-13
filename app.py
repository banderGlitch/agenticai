import streamlit as st  # type: ignore
import os
import json
import time
import networkx as nx
import matplotlib.pyplot as plt # type: ignore
from PIL import Image
from streamlit_agraph import agraph, Node, Edge, Config # type: ignore
from typing import Dict, Any, List
from main import create_sdlc_graph, SDLCState
from src.utils.visualize import visualize_graph, export_graph_json, track_execution

# Set page configuration
st.set_page_config(
    page_title="SDLC Agents",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.project_name = ""
    st.session_state.requirements = ""
    st.session_state.current_step = None
    st.session_state.workflow_state = None
    st.session_state.execution_history = {}
    st.session_state.graph = None
    st.session_state.graph_data = None
    st.session_state.workflow_started = False
    st.session_state.workflow_completed = False
    st.session_state.waiting_for_input = False
    st.session_state.input_type = None
    st.session_state.step_outputs = {}

# Function to initialize the workflow
def initialize_workflow():
    if st.session_state.project_name:
        # Initialize state
        initial_state = SDLCState(
            project_name=st.session_state.project_name,
            requirements=None,
            user_stories=None,
            design_documents=None,
            code=None,
            test_cases=None,
            deployment_status=None,
            monitoring_data=None,
            raw_requirements_input=st.session_state.requirements if st.session_state.requirements else None
        )
        
        # Create the workflow graph
        st.session_state.graph = create_sdlc_graph()
        
        # Get graph data for visualization
        try:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Generate visualization
            visualize_graph(st.session_state.graph)
            export_graph_json(st.session_state.graph)
            
            # Load graph data
            with open("output/workflow_graph.json", "r") as f:
                st.session_state.graph_data = json.load(f)
        except Exception as e:
            st.error(f"Error generating graph visualization: {e}")
        
        # Initialize workflow state
        st.session_state.workflow_state = initial_state
        st.session_state.initialized = True
        st.session_state.workflow_started = False
        st.session_state.workflow_completed = False
        st.session_state.execution_history = {}
        st.session_state.current_step = None
        st.session_state.step_outputs = {}
        
        st.success("Workflow initialized successfully!")
    else:
        st.error("Please enter a project name.")

# Function to run the next step in the workflow
def run_next_step():
    if not st.session_state.initialized:
        st.error("Please initialize the workflow first.")
        return
    
    if st.session_state.workflow_completed:
        st.info("Workflow has already completed.")
        return
    
    if st.session_state.waiting_for_input:
        st.warning("Please provide the required input before continuing.")
        return
    
    # Start or continue the workflow
    if not st.session_state.workflow_started:
        st.session_state.workflow_started = True
        # Create a generator for the workflow
        st.session_state.workflow_generator = st.session_state.graph.stream(st.session_state.workflow_state)
    
    try:
        # Get the next step
        step, state = next(st.session_state.workflow_generator)
        
        if step.name == "__end__":
            st.session_state.workflow_completed = True
            st.session_state.current_step = "Completed"
            
            # Save execution history
            try:
                track_execution(st.session_state.execution_history)
                st.success("Execution history saved to output/execution_history.json")
            except Exception as e:
                st.error(f"Error saving execution history: {e}")
            
            st.balloons()
            st.success("SDLC Workflow Completed!")
        else:
            # Update current step and state
            st.session_state.current_step = step.name
            st.session_state.workflow_state = state
            
            # Store state in execution history
            st.session_state.execution_history[step.name] = dict(state)
            
            # Check if we need user input for the next step
            if "review" in step.name and state.get("review_status") == "Pending User Approval":
                st.session_state.waiting_for_input = True
                st.session_state.input_type = "review"
            elif step.name == "gather_requirements" and not state.get("raw_requirements_input"):
                st.session_state.waiting_for_input = True
                st.session_state.input_type = "requirements"
            else:
                st.session_state.waiting_for_input = False
                st.session_state.input_type = None
            
            # Store step outputs for display
            for key, value in state.items():
                if value is not None and key not in st.session_state.step_outputs:
                    st.session_state.step_outputs[key] = value
    
    except StopIteration:
        st.session_state.workflow_completed = True
        st.session_state.current_step = "Completed"
        st.balloons()
        st.success("SDLC Workflow Completed!")
    except Exception as e:
        st.error(f"Error during workflow execution: {e}")

# Function to handle user input for reviews
def handle_review_input(decision):
    if decision == "Approved" or decision == "Needs Revision":
        # Update the state based on the decision
        if "review_user_stories" in st.session_state.current_step:
            from src.agents.review_agent import user_approve_review
            st.session_state.workflow_state = user_approve_review(st.session_state.workflow_state, decision)
        elif "review_design" in st.session_state.current_step:
            st.session_state.workflow_state["design_review_status"] = decision
        elif "review_code" in st.session_state.current_step:
            st.session_state.workflow_state["code_review_status"] = decision
        elif "review_test_cases" in st.session_state.current_step:
            st.session_state.workflow_state["test_review_status"] = decision
        
        # Continue workflow
        st.session_state.waiting_for_input = False
        st.session_state.input_type = None
        st.experimental_rerun()
    else:
        st.error("Invalid decision. Please select 'Approved' or 'Needs Revision'.")

# Function to handle requirements input
def handle_requirements_input(requirements):
    if requirements:
        st.session_state.workflow_state["raw_requirements_input"] = requirements
        st.session_state.waiting_for_input = False
        st.session_state.input_type = None
        st.experimental_rerun()
    else:
        st.error("Please enter requirements.")

# Function to visualize the workflow graph
def visualize_workflow_graph():
    if st.session_state.graph_data:
        # Create nodes and edges for agraph
        nodes = []
        edges = []
        
        # Add nodes
        for node in st.session_state.graph_data["nodes"]:
            color = "#1f77b4"  # Default color
            
            # Highlight current step
            if node == st.session_state.current_step:
                color = "#d62728"  # Red for current step
            # Highlight completed steps
            elif node in st.session_state.execution_history:
                color = "#2ca02c"  # Green for completed steps
            
            nodes.append(Node(id=node, label=node, color=color))
        
        # Add edges
        for edge in st.session_state.graph_data["edges"]:
            source = edge["source"]
            target = edge["target"]
            edges.append(Edge(source=source, target=target))
        
        # Configure the graph
        config = Config(
            width=700,
            height=500,
            directed=True,
            physics=True,
            hierarchical=False,
        )
        
        # Render the graph
        return agraph(nodes=nodes, edges=edges, config=config)
    else:
        try:
            # Try to display the static image
            image = Image.open("output/workflow_graph.png")
            return st.image(image, caption="SDLC Workflow Graph", use_column_width=True)
        except:
            st.warning("Workflow graph visualization not available.")
            return None

# Main app layout
def main():
    st.title("🔄 SDLC Agents - AI-Powered Software Development Lifecycle")
    
    # Sidebar
    with st.sidebar:
        st.header("Workflow Control")
        
        # Project setup
        st.subheader("Project Setup")
        project_name = st.text_input("Project Name", key="project_name_input", 
                                     value=st.session_state.project_name)
        
        requirements = st.text_area("Project Requirements", key="requirements_input", 
                                   value=st.session_state.requirements,
                                   help="Enter the requirements for your project. Leave blank to enter during workflow.")
        
        if st.button("Initialize Workflow"):
            st.session_state.project_name = project_name
            st.session_state.requirements = requirements
            initialize_workflow()
        
        # Workflow control
        st.subheader("Workflow Control")
        
        if st.button("Run Next Step", disabled=not st.session_state.initialized or st.session_state.workflow_completed):
            run_next_step()
        
        if st.button("Run Complete Workflow", disabled=not st.session_state.initialized or st.session_state.workflow_completed):
            # Run until completion or until user input is required
            while not st.session_state.workflow_completed and not st.session_state.waiting_for_input:
                run_next_step()
            st.experimental_rerun()
        
        # Workflow status
        st.subheader("Workflow Status")
        st.write(f"Current Step: {st.session_state.current_step if st.session_state.current_step else 'Not started'}")
        st.write(f"Status: {'Completed' if st.session_state.workflow_completed else 'In Progress' if st.session_state.workflow_started else 'Not Started'}")
    
    # Main content area - two columns
    col1, col2 = st.columns([3, 2])
    
    # Left column - Workflow visualization and user input
    with col1:
        st.header("SDLC Workflow")
        
        # Workflow visualization
        visualize_workflow_graph()
        
        # User input section
        if st.session_state.waiting_for_input:
            st.header("User Input Required")
            
            if st.session_state.input_type == "review":
                st.subheader(f"Review: {st.session_state.current_step}")
                
                # Display review feedback
                if "review_feedback" in st.session_state.workflow_state:
                    st.text_area("Review Feedback", value=st.session_state.workflow_state["review_feedback"], height=200, disabled=True)
                
                # Review decision
                decision = st.radio("Decision", ["Approved", "Needs Revision"])
                
                if st.button("Submit Decision"):
                    handle_review_input(decision)
            
            elif st.session_state.input_type == "requirements":
                st.subheader("Enter Project Requirements")
                requirements = st.text_area("Requirements", height=200)
                
                if st.button("Submit Requirements"):
                    handle_requirements_input(requirements)
    
    # Right column - Step outputs and artifacts
    with col2:
        st.header("Artifacts & Outputs")
        
        # Display step outputs in tabs
        if st.session_state.step_outputs:
            tabs = st.tabs(["Requirements", "User Stories", "Design", "Code", "Tests", "Deployment"])
            
            # Requirements tab
            with tabs[0]:
                if "requirements" in st.session_state.step_outputs:
                    st.subheader("Project Requirements")
                    if isinstance(st.session_state.step_outputs["requirements"], dict):
                        st.json(st.session_state.step_outputs["requirements"])
                    else:
                        st.text_area("Requirements", value=st.session_state.step_outputs["requirements"], height=300, disabled=True)
                else:
                    st.info("Requirements not generated yet.")
            
            # User Stories tab
            with tabs[1]:
                if "user_stories" in st.session_state.step_outputs:
                    st.subheader("User Stories")
                    st.text_area("User Stories", value=st.session_state.step_outputs["user_stories"], height=300, disabled=True)
                    
                    if "review_feedback" in st.session_state.step_outputs:
                        st.subheader("Review Feedback")
                        st.text_area("Feedback", value=st.session_state.step_outputs["review_feedback"], height=150, disabled=True)
                else:
                    st.info("User stories not generated yet.")
            
            # Design tab
            with tabs[2]:
                if "design_documents" in st.session_state.step_outputs:
                    st.subheader("Design Documents")
                    st.text_area("Design", value=st.session_state.step_outputs["design_documents"], height=300, disabled=True)
                    
                    if "design_review_feedback" in st.session_state.step_outputs:
                        st.subheader("Design Review Feedback")
                        st.text_area("Feedback", value=st.session_state.step_outputs["design_review_feedback"], height=150, disabled=True)
                else:
                    st.info("Design documents not generated yet.")
            
            # Code tab
            with tabs[3]:
                if "code" in st.session_state.step_outputs:
                    st.subheader("Generated Code")
                    st.text_area("Code", value=st.session_state.step_outputs["code"], height=300, disabled=True)
                    
                    if "code_review_feedback" in st.session_state.step_outputs:
                        st.subheader("Code Review Feedback")
                        st.text_area("Feedback", value=st.session_state.step_outputs["code_review_feedback"], height=150, disabled=True)
                else:
                    st.info("Code not generated yet.")
            
            # Tests tab
            with tabs[4]:
                if "test_cases" in st.session_state.step_outputs:
                    st.subheader("Test Cases")
                    st.text_area("Tests", value=st.session_state.step_outputs["test_cases"], height=300, disabled=True)
                    
                    if "qa_results" in st.session_state.step_outputs:
                        st.subheader("QA Results")
                        st.text_area("Results", value=st.session_state.step_outputs["qa_results"], height=150, disabled=True)
                else:
                    st.info("Test cases not generated yet.")
            
            # Deployment tab
            with tabs[5]:
                if "deployment_plan" in st.session_state.step_outputs:
                    st.subheader("Deployment Plan")
                    st.text_area("Plan", value=st.session_state.step_outputs["deployment_plan"], height=300, disabled=True)
                    
                    if "deployment_status" in st.session_state.step_outputs:
                        st.subheader("Deployment Status")
                        st.success(st.session_state.step_outputs["deployment_status"])
                else:
                    st.info("Deployment plan not generated yet.")

# Run the app
if __name__ == "__main__":
    main() 