import streamlit as st
import os
import json
from typing import Dict, Any, List
from main import create_sdlc_graph, SDLCState

# Set page configuration
st.set_page_config(
    page_title="SDLC Agents - Simple Workflow",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to improve spacing and reduce congestion
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    .workflow-step {
        padding: 8px;
        border-radius: 5px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
    }
    .step-number {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        flex-shrink: 0;
    }
    .step-connector {
        width: 2px;
        height: 10px;
        background-color: #ccc;
        margin-left: 12px;
    }
    .main-header {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.project_name = ""
    st.session_state.requirements = ""
    st.session_state.current_step = None
    st.session_state.workflow_state = None
    st.session_state.execution_history = {}
    st.session_state.step_number = 0
    st.session_state.total_steps = 7  # Total number of steps in our workflow

# Define the steps in our workflow for display purposes
WORKFLOW_STEPS = [
    "Requirements Gathering",
    "User Story Generation",
    "Design Creation",
    "Code Generation",
    "Test Case Writing",
    "QA Testing",
    "Deployment"
]

def initialize_workflow():
    """Initialize the workflow with the project name and requirements"""
    if not st.session_state.project_name:
        st.error("Please enter a project name")
        return
    
    # Create initial state
    initial_state = SDLCState(
        project_name=st.session_state.project_name,
        requirements=st.session_state.requirements,
        user_stories=None,
        design_documents=None,
        code=None,
        test_cases=None,
        qa_results=None,
        deployment_status=None
    )
    
    # Create the workflow graph
    try:
        st.session_state.graph = create_sdlc_graph()
        
        # Create the workflow iterator
        # The stream method returns (node, state) tuples
        st.session_state.workflow_iterator = st.session_state.graph.stream(initial_state)
        
        # Set initial state
        st.session_state.current_step = "START"
        st.session_state.workflow_state = initial_state
        st.session_state.initialized = True
        st.session_state.step_number = 0
        st.session_state.execution_history = {}
        
        st.success("Workflow initialized! Click 'Run Next Step' to begin the SDLC process.")
    except Exception as e:
        st.error(f"Error initializing workflow: {e}")
        import traceback
        st.error(traceback.format_exc())

def run_next_step():
    """Run the next step in the workflow"""
    if not st.session_state.initialized:
        st.error("Please initialize the workflow first")
        return
    
    try:
        # Get the next step from the iterator
        result = next(st.session_state.workflow_iterator)
        
        # Handle AddableUpdatesDict format from LangGraph
        if hasattr(result, 'keys') and len(result) > 0:
            # This is a dictionary-like object with node names as keys
            # Get the first key as the step name
            step_name = list(result.keys())[0]
            
            # Get the state from the value
            state_updates = result[step_name]
            
            # Update the current state with the new values
            if isinstance(state_updates, dict):
                # Create a new state by updating the current one
                current_state = st.session_state.workflow_state or {}
                state = {**current_state, **state_updates}
            else:
                # If it's not a dict, just use it as is
                state = state_updates
                
            # Update session state
            st.session_state.current_step = step_name
            st.session_state.workflow_state = state
            
            # Store in execution history
            st.session_state.execution_history[step_name] = dict(state) if isinstance(state, dict) else state
            
            # Increment step number
            st.session_state.step_number += 1
            
            # Display success message
            step_index = min(st.session_state.step_number - 1, len(WORKFLOW_STEPS) - 1)
            step_name_display = WORKFLOW_STEPS[step_index] if step_index >= 0 else step_name
            st.success(f"✅ Completed step: {step_name_display}")
            
        elif isinstance(result, tuple) and len(result) == 2:
            # Standard format: (node, state)
            step, state = result
            step_name = getattr(step, 'name', str(step))
            
            # Update session state
            st.session_state.current_step = step_name
            st.session_state.workflow_state = state
            
            # Store in execution history if it's a dictionary
            if isinstance(state, dict):
                st.session_state.execution_history[step_name] = dict(state)
            
            # Increment step number if not at the end
            if step_name != "__end__":
                st.session_state.step_number += 1
            
            # If we've reached the end, show a completion message
            if step_name == "__end__":
                st.balloons()
                st.success("🎉 SDLC Workflow Completed! Your software development lifecycle is complete.")
            else:
                # Make sure we don't go out of bounds
                step_index = min(st.session_state.step_number - 1, len(WORKFLOW_STEPS) - 1)
                step_name_display = WORKFLOW_STEPS[step_index] if step_index >= 0 else step_name
                st.success(f"✅ Completed step: {step_name_display}")
        else:
            # Unknown format
            st.error(f"Unexpected result format from workflow: {result}")
            return
            
    except StopIteration:
        st.info("Workflow has completed. No more steps to run.")
        st.balloons()
        st.success("🎉 SDLC Workflow Completed! Your software development lifecycle is complete.")
    except Exception as e:
        st.error(f"Error running step: {e}")
        import traceback
        st.error(traceback.format_exc())

def handle_requirements_input(requirements):
    """Handle the requirements input from the user"""
    st.session_state.requirements = requirements

def render_compact_workflow():
    """Render a more compact workflow diagram"""
    # Create a horizontal layout for the workflow steps
    cols = st.columns(len(WORKFLOW_STEPS))
    
    for i, (col, step) in enumerate(zip(cols, WORKFLOW_STEPS)):
        with col:
            # Determine step status
            if i < st.session_state.step_number:
                status = "✅"
                bg_color = "#e6f4ea"  # Light green
                text_color = "#137333"  # Dark green
            elif i == st.session_state.step_number:
                status = "🔄"
                bg_color = "#fef7e0"  # Light yellow
                text_color = "#b06000"  # Dark yellow/orange
            else:
                status = "⏳"
                bg_color = "#f8f9fa"  # Light gray
                text_color = "#5f6368"  # Dark gray
            
            # Render step with number and status
            st.markdown(f"""
            <div style="
                background-color: {bg_color};
                color: {text_color};
                padding: 8px 4px;
                border-radius: 4px;
                text-align: center;
                height: 100%;
                font-size: 0.8rem;
            ">
                <div style="font-weight: bold;">{i+1}. {status}</div>
                <div>{step.split()[0]}</div>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main function for the Streamlit app"""
    # Title with reduced size
    st.markdown('<h1 style="font-size: 1.8rem;">🔄 SDLC Agents - Software Development Workflow</h1>', unsafe_allow_html=True)
    
    # Sidebar for project setup
    with st.sidebar:
        st.markdown('<h2 class="main-header">Project Setup</h2>', unsafe_allow_html=True)
        
        # Project name input
        st.markdown('<h3 class="sub-header">Project Name</h3>', unsafe_allow_html=True)
        project_name = st.text_input("Enter your project name", value=st.session_state.project_name, label_visibility="collapsed")
        if project_name != st.session_state.project_name:
            st.session_state.project_name = project_name
        
        # Project requirements input
        st.markdown('<h3 class="sub-header">Project Requirements</h3>', unsafe_allow_html=True)
        requirements = st.text_area("Describe what you want to build", 
                                   value=st.session_state.requirements, 
                                   height=150,
                                   placeholder="Example: A snake game with score tracking and multiple difficulty levels",
                                   label_visibility="collapsed")
        if requirements != st.session_state.requirements:
            handle_requirements_input(requirements)
        
        # Initialize workflow button
        if st.button("Initialize Workflow", use_container_width=True):
            initialize_workflow()
        
        # Workflow control section
        if st.session_state.initialized:
            st.markdown('<h2 class="main-header">Workflow Control</h2>', unsafe_allow_html=True)
            if st.button("Run Next Step", use_container_width=True):
                run_next_step()
    
    # Main content area
    if st.session_state.initialized:
        # Compact description
        st.markdown("""
        <div style="font-size: 0.9rem; color: #5f6368; margin-bottom: 1rem;">
            This app demonstrates a simplified Software Development Life Cycle (SDLC) workflow using AI agents.
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress = min(st.session_state.step_number / st.session_state.total_steps, 1.0)
        st.progress(progress)
        
        # Compact workflow diagram
        render_compact_workflow()
        
        # Tabs for artifacts
        st.markdown('<h2 style="font-size: 1.3rem; margin-top: 1rem;">Project Artifacts</h2>', unsafe_allow_html=True)
        
        # Display the current state in tabs
        state = st.session_state.workflow_state
        
        # Create tabs for different artifacts
        tabs = st.tabs([
            "Requirements", 
            "User Stories", 
            "Design", 
            "Code", 
            "Tests", 
            "QA", 
            "Deployment"
        ])
        
        # Requirements tab
        with tabs[0]:
            if state.get("requirements"):
                st.text_area("Requirements", value=state["requirements"], height=300, disabled=True, label_visibility="collapsed")
            else:
                st.info("Requirements not generated yet.")
        
        # User Stories tab
        with tabs[1]:
            if state.get("user_stories"):
                st.text_area("User Stories", value=state["user_stories"], height=300, disabled=True, label_visibility="collapsed")
            else:
                st.info("User stories not generated yet.")
        
        # Design Documents tab
        with tabs[2]:
            if state.get("design_documents"):
                st.text_area("Design", value=state["design_documents"], height=300, disabled=True, label_visibility="collapsed")
            else:
                st.info("Design documents not generated yet.")
        
        # Code tab
        with tabs[3]:
            if state.get("code"):
                st.code(state["code"])
            else:
                st.info("Code not generated yet.")
        
        # Tests tab
        with tabs[4]:
            if state.get("test_cases"):
                st.text_area("Tests", value=state["test_cases"], height=300, disabled=True, label_visibility="collapsed")
            else:
                st.info("Test cases not generated yet.")
        
        # QA Results tab
        with tabs[5]:
            if state.get("qa_results"):
                st.text_area("QA", value=state["qa_results"], height=300, disabled=True, label_visibility="collapsed")
            else:
                st.info("QA results not generated yet.")
        
        # Deployment tab
        with tabs[6]:
            if state.get("deployment_status"):
                st.text_area("Deployment", value=state["deployment_status"], height=300, disabled=True, label_visibility="collapsed")
            else:
                st.info("Deployment status not generated yet.")
    else:
        # Welcome message for users who haven't initialized yet
        st.markdown("""
        <div style="padding: 2rem; text-align: center; background-color: #f8f9fa; border-radius: 10px;">
            <h2>Welcome to SDLC Agents</h2>
            <p>This app demonstrates a simplified Software Development Life Cycle workflow using AI agents.</p>
            <p>To get started:</p>
            <ol style="text-align: left; display: inline-block;">
                <li>Enter a project name in the sidebar</li>
                <li>Describe your project requirements</li>
                <li>Click "Initialize Workflow" to begin</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 