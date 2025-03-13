from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_test_case_prompt():
    return PromptTemplate(
        input_variables=["code", "user_stories"],
        template="""
        You are a QA engineer. Based on the following code and user stories,
        write comprehensive test cases:
        
        User Stories:
        {user_stories}
        
        Code:
        {code}
        
        Please provide:
        
        1. Unit Tests
           - Test each function/method
           - Include positive and negative test cases
           - Test edge cases
        
        2. Integration Tests
           - Test interactions between components
           - Test API endpoints
           - Test database operations
        
        3. End-to-End Tests
           - Test complete user workflows
           - Test UI interactions if applicable
        
        For each test case, include:
        - Test ID
        - Test description
        - Preconditions
        - Test steps
        - Expected results
        - Test data
        - Test code implementation
        
        Organize tests by component/feature and prioritize them.
        """
    )

def get_test_review_prompt():
    return PromptTemplate(
        input_variables=["test_cases"],
        template="""
        Review the following test cases:
        
        {test_cases}
        
        Provide feedback on:
        1. Coverage - Do the tests cover all requirements and code paths?
        2. Completeness - Are all test scenarios included?
        3. Quality - Are the tests well-designed and maintainable?
        4. Edge cases - Are edge cases properly tested?
        5. Negative testing - Are failure scenarios tested?
        
        If the test cases meet all criteria, respond with 'Approved'.
        Otherwise, suggest specific improvements and mark as 'Needs Revision'.
        """
    )

def get_test_fix_prompt():
    return PromptTemplate(
        input_variables=["test_cases", "review_feedback"],
        template="""
        You need to fix the following test cases based on the review feedback:
        
        Original Test Cases:
        {test_cases}
        
        Review Feedback:
        {review_feedback}
        
        Please provide:
        1. Updated test cases addressing all feedback points
        2. Explanation of the changes made
        
        For each test case, include:
        - Test ID
        - Test description
        - Preconditions
        - Test steps
        - Expected results
        - Test data
        - Test code implementation
        """
    )

def write_test_cases(state):
    """
    Write test cases based on code and user stories
    """
    test_chain = LLMChain(llm=get_groq_llm(), prompt=get_test_case_prompt())
    test_cases = test_chain.run(
        code=state["code"],
        user_stories=state["user_stories"]
    )
    
    state["test_cases"] = test_cases
    
    # Save test cases to file
    os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)
    with open(f"{PROJECT_CONFIG['output_dir']}/test_cases.md", "w") as f:
        f.write(test_cases)
    
    # Parse and save actual test code files
    try:
        test_dir = f"{PROJECT_CONFIG['output_dir']}/tests"
        os.makedirs(test_dir, exist_ok=True)
        
        # Simple parser to extract files from the markdown
        lines = test_cases.split('\n')
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
                    file_path = os.path.join(test_dir, current_file)
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
        print(f"Error extracting test files: {e}")
    
    print("Test cases written successfully.")
    return state

def review_test_cases(state):
    """
    Review the test cases
    """
    review_chain = LLMChain(llm=get_groq_llm(), prompt=get_test_review_prompt())
    feedback = review_chain.run(test_cases=state["test_cases"])
    
    state["test_review_feedback"] = feedback
    
    if "Approved" in feedback:
        state["test_review_status"] = "Approved"
        print("Test review: Approved")
    else:
        state["test_review_status"] = "Needs Revision"
        print("Test review: Needs Revision")
        print("Feedback:", feedback)
    
    # Save test review feedback to file
    with open(f"{PROJECT_CONFIG['output_dir']}/test_review.md", "w") as f:
        f.write(feedback)
    
    return state

def fix_test_cases(state):
    """
    Fix test cases based on review feedback
    """
    fix_chain = LLMChain(llm=get_groq_llm(), prompt=get_test_fix_prompt())
    fixed_tests = fix_chain.run(
        test_cases=state["test_cases"],
        review_feedback=state["test_review_feedback"]
    )
    
    state["fixed_test_cases"] = fixed_tests
    state["test_cases"] = fixed_tests  # Update the main test cases
    state["test_review_status"] = "Fixed"
    
    # Save fixed test cases to file
    with open(f"{PROJECT_CONFIG['output_dir']}/fixed_test_cases.md", "w") as f:
        f.write(fixed_tests)
    
    # Parse and save actual test code files
    try:
        test_dir = f"{PROJECT_CONFIG['output_dir']}/tests"
        os.makedirs(test_dir, exist_ok=True)
        
        # Simple parser to extract files from the markdown
        lines = fixed_tests.split('\n')
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
                    file_path = os.path.join(test_dir, current_file)
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
        print(f"Error extracting fixed test files: {e}")
    
    print("Test cases fixed successfully.")
    return state 