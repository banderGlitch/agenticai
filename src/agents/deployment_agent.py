from langchain_core.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_deployment_prompt():
    return PromptTemplate(
        input_variables=["code", "project_name"],
        template="""
        You are a DevOps engineer. Create a deployment plan and configuration for the project named "{project_name}".
        
        Code:
        {code}
        
        Please provide:
        
        1. Deployment Strategy
           - Recommended deployment approach (e.g., containerization, serverless, traditional hosting)
           - Environment setup (dev, staging, production)
           - CI/CD pipeline configuration
        
        2. Infrastructure as Code
           - Docker configuration (if applicable)
           - Kubernetes manifests (if applicable)
           - Terraform/CloudFormation templates (if applicable)
           - Serverless configuration (if applicable)
        
        3. Deployment Instructions
           - Step-by-step deployment guide
           - Required environment variables
           - Database migration steps (if applicable)
           - Rollback procedures
        
        4. Monitoring and Logging Setup
           - Recommended monitoring tools
           - Log aggregation configuration
           - Alert setup recommendations
        
        Provide all necessary configuration files and scripts for deployment.
        """
    )

def deploy_application(state):
    """
    Create deployment configuration and instructions
    """
    deployment_chain = LLMChain(llm=get_groq_llm(), prompt=get_deployment_prompt())
    deployment_plan = deployment_chain.run(
        code=state["code"],
        project_name=state["project_name"]
    )
    
    state["deployment_plan"] = deployment_plan
    state["deployment_status"] = "Ready for Deployment"
    
    # Save deployment plan to file
    os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)
    with open(f"{PROJECT_CONFIG['output_dir']}/deployment_plan.md", "w") as f:
        f.write(deployment_plan)
    
    # Parse and save deployment configuration files
    try:
        deploy_dir = f"{PROJECT_CONFIG['output_dir']}/deployment"
        os.makedirs(deploy_dir, exist_ok=True)
        
        # Simple parser to extract files from the markdown
        lines = deployment_plan.split('\n')
        current_file = None
        file_content = []
        in_code_block = False
        
        for line in lines:
            if line.startswith('```') and not in_code_block:
                in_code_block = True
                # Extract filename if present
                if len(line) > 3:
                    current_file = line[3:].strip()
                continue
            elif line.startswith('```') and in_code_block:
                in_code_block = False
                if current_file:
                    # Create directories if needed
                    file_path = os.path.join(deploy_dir, current_file)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Write file content
                    with open(file_path, 'w') as f:
                        f.write('\n'.join(file_content))
                    
                    file_content = []
                    current_file = None
                continue
            
            if in_code_block and current_file:
                file_content.append(line)
    
    except Exception as e:
        print(f"Error extracting deployment files: {e}")
    
    print("Deployment plan created successfully.")
    
    # Simulate deployment
    print("\nSimulating deployment...")
    print("Deployment successful!")
    state["deployment_status"] = "Deployed"
    
    return state 