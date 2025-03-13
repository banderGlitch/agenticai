from langchain_core.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
import json
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_code_generation_prompt():
    return PromptTemplate(
        input_variables=["design_documents", "project_name"],
        template="""
        You are an expert software developer. Based on the following design documents,
        generate code for the project named "{project_name}".
        
        Design Documents:
        {design_documents}
        
        Please provide:
        
        1. Project structure (directory layout)
        2. Key files with complete code implementations
        3. Dependencies and configuration files
        4. README.md with setup and usage instructions
        
        For each file, include:
        - File path
        - Complete code content
        - Brief explanation of what the code does
        
        Focus on creating working, production-quality code that implements all the requirements.
        """
    )

def get_code_review_prompt():
    return PromptTemplate(
        input_variables=["code"],
        template="""
        Review the following code:
        
        {code}
        
        Provide feedback on:
        1. Correctness - Does it work as expected?
        2. Code quality - Is it well-structured and maintainable?
        3. Performance - Are there any performance concerns?
        4. Security - Are there any security vulnerabilities?
        5. Best practices - Does it follow industry best practices?
        
        For each issue found, specify:
        - The file and line number
        - The issue description
        - A suggested fix
        
        If the code meets all criteria, respond with 'Approved'.
        Otherwise, list all issues and mark as 'Needs Revision'.
        """
    )

def get_code_fix_prompt():
    return PromptTemplate(
        input_variables=["code", "review_feedback"],
        template="""
        You need to fix the following code based on the review feedback:
        
        Original Code:
        {code}
        
        Review Feedback:
        {review_feedback}
        
        Please provide:
        1. Updated code for each file that needs changes
        2. Explanation of the changes made
        
        For each file, include:
        - File path
        - Complete updated code content
        - Brief explanation of the changes
        """
    )

def generate_code(state):
    """
    Generate code based on design documents
    """
    code_chain = LLMChain(llm=get_groq_llm(), prompt=get_code_generation_prompt())
    code_output = code_chain.run(
        design_documents=state["design_documents"],
        project_name=state["project_name"]
    )
    
    state["code"] = code_output
    
    # Save code to file
    os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)
    with open(f"{PROJECT_CONFIG['output_dir']}/generated_code.md", "w") as f:
        f.write(code_output)
    
    # Parse and save actual code files
    try:
        code_dir = f"{PROJECT_CONFIG['output_dir']}/code"
        os.makedirs(code_dir, exist_ok=True)
        
        # Simple parser to extract files from the markdown
        lines = code_output.split('\n')
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
                    file_path = os.path.join(code_dir, current_file)
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
        print(f"Error extracting code files: {e}")
    
    print("Code generated successfully.")
    return state

def review_code(state):
    """
    Review the generated code
    """
    review_chain = LLMChain(llm=get_groq_llm(), prompt=get_code_review_prompt())
    feedback = review_chain.run(code=state["code"])
    
    state["code_review_feedback"] = feedback
    
    if "Approved" in feedback:
        state["code_review_status"] = "Approved"
        print("Code review: Approved")
    else:
        state["code_review_status"] = "Needs Revision"
        print("Code review: Needs Revision")
        print("Feedback:", feedback)
    
    # Save review feedback to file
    with open(f"{PROJECT_CONFIG['output_dir']}/code_review.md", "w") as f:
        f.write(feedback)
    
    return state

def fix_code_after_review(state):
    """
    Fix code based on review feedback
    """
    fix_chain = LLMChain(llm=get_groq_llm(), prompt=get_code_fix_prompt())
    fixed_code = fix_chain.run(
        code=state["code"],
        review_feedback=state["code_review_feedback"]
    )
    
    state["fixed_code"] = fixed_code
    state["code"] = fixed_code  # Update the main code
    state["code_review_status"] = "Fixed"
    
    # Save fixed code to file
    with open(f"{PROJECT_CONFIG['output_dir']}/fixed_code.md", "w") as f:
        f.write(fixed_code)
    
    # Parse and save actual code files (similar to generate_code)
    try:
        code_dir = f"{PROJECT_CONFIG['output_dir']}/code"
        os.makedirs(code_dir, exist_ok=True)
        
        # Simple parser to extract files from the markdown
        lines = fixed_code.split('\n')
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
                    file_path = os.path.join(code_dir, current_file)
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
        print(f"Error extracting fixed code files: {e}")
    
    print("Code fixed successfully.")
    return state 