from langchain_core.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_security_review_prompt():
    return PromptTemplate(
        input_variables=["code"],
        template="""
        You are a cybersecurity expert. Perform a comprehensive security review of the following code:
        
        {code}
        
        Focus on identifying:
        1. Injection vulnerabilities (SQL, NoSQL, command, etc.)
        2. Authentication and authorization issues
        3. Sensitive data exposure
        4. XML External Entities (XXE)
        5. Broken access control
        6. Security misconfiguration
        7. Cross-Site Scripting (XSS)
        8. Insecure deserialization
        9. Using components with known vulnerabilities
        10. Insufficient logging and monitoring
        
        For each vulnerability found:
        - Specify the file and line number
        - Describe the vulnerability
        - Rate the severity (Critical, High, Medium, Low)
        - Provide a recommended fix
        
        If no security issues are found, respond with 'Approved'.
        Otherwise, list all vulnerabilities and mark as 'Needs Security Fixes'.
        """
    )

def get_security_fix_prompt():
    return PromptTemplate(
        input_variables=["code", "security_feedback"],
        template="""
        You need to fix the following security vulnerabilities in the code:
        
        Original Code:
        {code}
        
        Security Review Feedback:
        {security_feedback}
        
        Please provide:
        1. Updated code for each file that needs security fixes
        2. Explanation of the security fixes implemented
        
        For each file, include:
        - File path
        - Complete updated code content
        - Brief explanation of the security changes
        """
    )

def security_review(state):
    """
    Perform a security review of the code
    """
    security_chain = LLMChain(llm=get_groq_llm(), prompt=get_security_review_prompt())
    security_feedback = security_chain.run(code=state["code"])
    
    state["security_review_feedback"] = security_feedback
    
    if "Approved" in security_feedback:
        state["security_review_status"] = "Approved"
        print("Security review: Approved")
    else:
        state["security_review_status"] = "Needs Security Fixes"
        print("Security review: Needs Security Fixes")
        print("Security Feedback:", security_feedback)
    
    # Save security review feedback to file
    with open(f"{PROJECT_CONFIG['output_dir']}/security_review.md", "w") as f:
        f.write(security_feedback)
    
    return state

def fix_code_after_security(state):
    """
    Fix code based on security review feedback
    """
    fix_chain = LLMChain(llm=get_groq_llm(), prompt=get_security_fix_prompt())
    security_fixed_code = fix_chain.run(
        code=state["code"],
        security_feedback=state["security_review_feedback"]
    )
    
    state["security_fixed_code"] = security_fixed_code
    state["code"] = security_fixed_code  # Update the main code
    state["security_review_status"] = "Fixed"
    
    # Save security fixed code to file
    with open(f"{PROJECT_CONFIG['output_dir']}/security_fixed_code.md", "w") as f:
        f.write(security_fixed_code)
    
    # Parse and save actual code files (similar to code_agent)
    try:
        code_dir = f"{PROJECT_CONFIG['output_dir']}/code"
        os.makedirs(code_dir, exist_ok=True)
        
        # Simple parser to extract files from the markdown
        lines = security_fixed_code.split('\n')
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
        print(f"Error extracting security fixed code files: {e}")
    
    print("Security issues fixed successfully.")
    return state 