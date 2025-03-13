from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_maintenance_prompt():
    return PromptTemplate(
        input_variables=["project_name", "monitoring_data", "code", "user_stories"],
        template="""
        You are a software maintenance engineer. Based on the monitoring data and user feedback,
        create a maintenance and update plan for the project named "{project_name}".
        
        Original User Stories:
        {user_stories}
        
        Current Code:
        {code}
        
        Monitoring Data and User Feedback:
        {monitoring_data}
        
        Please provide:
        
        1. Issue Analysis
           - Identify potential issues based on monitoring data
           - Prioritize issues by severity and impact
           - Root cause analysis for critical issues
        
        2. Improvement Recommendations
           - Feature enhancements based on user feedback
           - Performance optimizations
           - Security updates
        
        3. Maintenance Schedule
           - Regular maintenance tasks
           - Update roadmap
           - Technical debt reduction plan
        
        4. Update Implementation Plan
           - Code changes needed for high-priority updates
           - Testing strategy for updates
           - Rollout strategy
        
        Provide a comprehensive maintenance and update plan that addresses current issues and improves the application over time.
        """
    )

def maintain_application(state):
    """
    Create maintenance and update plan
    """
    # Convert monitoring data to string if it's a dict
    monitoring_data_str = str(state["monitoring_data"])
    
    maintenance_chain = LLMChain(llm=get_groq_llm(), prompt=get_maintenance_prompt())
    maintenance_plan = maintenance_chain.run(
        project_name=state["project_name"],
        monitoring_data=monitoring_data_str,
        code=state["code"],
        user_stories=state["user_stories"]
    )
    
    state["maintenance_plan"] = maintenance_plan
    
    # Save maintenance plan to file
    os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)
    with open(f"{PROJECT_CONFIG['output_dir']}/maintenance_plan.md", "w") as f:
        f.write(maintenance_plan)
    
    print("Maintenance and update plan created successfully.")
    
    # Create a project summary
    create_project_summary(state)
    
    return state

def create_project_summary(state):
    """
    Create a summary of the entire project
    """
    summary = f"""
# {state['project_name']} - Project Summary

## Project Overview
This project was developed using an AI-powered SDLC workflow.

## Development Artifacts

### Requirements
- Requirements document created
- File: output/requirements.json

### User Stories
- User stories generated and approved
- File: output/user_stories.md

### Design
- Design documents created and reviewed
- File: output/design_documents.md

### Code
- Code generated, reviewed, and fixed
- Directory: output/code/

### Tests
- Test cases written, reviewed, and fixed
- Directory: output/tests/

### Deployment
- Deployment plan created
- File: output/deployment_plan.md
- Status: {state.get('deployment_status', 'Unknown')}

### Monitoring
- Monitoring plan established
- File: output/monitoring_plan.md

### Maintenance
- Maintenance and update plan created
- File: output/maintenance_plan.md

## Next Steps
1. Review the maintenance plan
2. Implement recommended updates
3. Continue monitoring application performance
4. Gather additional user feedback
5. Plan next iteration of development
    """
    
    with open(f"{PROJECT_CONFIG['output_dir']}/project_summary.md", "w") as f:
        f.write(summary)
    
    print("\nProject summary created.")
    print(f"All project artifacts are available in the '{PROJECT_CONFIG['output_dir']}' directory.") 