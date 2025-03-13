from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_qa_testing_prompt():
    return PromptTemplate(
        input_variables=["code", "test_cases"],
        template="""
        You are a QA tester. Simulate running the test cases on the provided code and report the results:
        
        Code:
        {code}
        
        Test Cases:
        {test_cases}
        
        For each test case:
        1. Analyze if the code would pass or fail the test
        2. Provide detailed reasoning for your conclusion
        3. If a test would fail, explain why and what part of the code is problematic
        
        Summarize the overall test results:
        - Total tests
        - Passed tests
        - Failed tests
        - Pass rate percentage
        
        If all tests pass, respond with 'QA Testing: Passed'.
        Otherwise, list all failed tests and respond with 'QA Testing: Failed'.
        """
    )

def get_qa_fix_prompt():
    return PromptTemplate(
        input_variables=["code", "qa_feedback"],
        template="""
        You need to fix the following code based on QA testing feedback:
        
        Original Code:
        {code}
        
        QA Testing Feedback:
        {qa_feedback}
        
        Please provide:
        1. Updated code that fixes all the issues identified in QA testing
        2. Explanation of the fixes implemented
        
        For each file, include:
        - File path
        - Complete updated code content
        - Brief explanation of the changes
        """
    )

def qa_testing(state):
    """
    Perform QA testing on the code using the test cases
    """
    qa_chain = LLMChain(llm=get_groq_llm(), prompt=get_qa_testing_prompt())
    qa_results = qa_chain.run(
        code=state["code"],
        test_cases=state["test_cases"]
    )
    
    state["qa_results"] = qa_results
    
    if "QA Testing: Passed" in qa_results:
        state["qa_status"] = "Passed"
        print("QA Testing: Passed")
    else:
        state["qa_status"] = "Failed"
        print("QA Testing: Failed")
        print("QA Feedback:", qa_results)
    
    # Save QA results to file
    with open(f"{PROJECT_CONFIG['output_dir']}/qa_results.md", "w") as f:
        f.write(qa_results)
    
    return state

def fix_code_after_qa(state):
    """
    Fix code based on QA testing feedback
    """
    fix_chain = LLMChain(llm=get_groq_llm(), prompt=get_qa_fix_prompt())
    qa_fixed_code = fix_chain.run(
        code=state["code"],
        qa_feedback=state["qa_results"]
    )
    
    state["qa_fixed_code"] = qa_fixed_code
    state["code"] = qa_fixed_code  # Update the main code
    
    # Save QA fixed code to file
    with open(f"{PROJECT_CONFIG['output_dir']}/qa_fixed_code.md", "w") as f:
        f.write(qa_fixed_code)
    
    # Parse and save actual code files
    try:
        code_dir = f"{PROJECT_CONFIG['output_dir']}/code"
        os.makedirs(code_dir, exist_ok=True)
        
        # Simple parser to extract files from the markdown
        lines = qa_fixed_code.split('\n')
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
        print(f"Error extracting QA fixed code files: {e}")
    
    print("Code fixed after QA testing.")
    return state 