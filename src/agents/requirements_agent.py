from langchain_core.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
import json
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_requirements_prompt():
    return PromptTemplate(
        input_variables=["user_input"],
        template="""
        You are a requirements analysis expert. Based on the following user input, 
        extract and organize the software requirements.
        
        User Input:
        "{user_input}"
        
        Please provide:
        1. Functional Requirements (what the system should do)
        2. Non-Functional Requirements (performance, security, usability, etc.)
        3. Constraints (technical, business, or regulatory limitations)
        4. Assumptions (what we're assuming to be true)
        
        Format your response as a structured JSON with these categories.
        """
    )

def gather_requirements(state):
    """
    Gather and process user requirements
    """
    print("Please describe your project requirements:")
    user_input = input("> ")
    
    # Save raw user input
    state["raw_requirements_input"] = user_input
    
    # Process requirements with LLM
    requirements_chain = LLMChain(llm=get_groq_llm(), prompt=get_requirements_prompt())
    processed_requirements = requirements_chain.run(user_input=user_input)
    
    try:
        # Try to parse as JSON
        requirements_json = json.loads(processed_requirements)
        state["requirements"] = requirements_json
    except json.JSONDecodeError:
        # If not valid JSON, store as text
        state["requirements"] = processed_requirements
    
    # Save requirements to file
    os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)
    with open(f"{PROJECT_CONFIG['output_dir']}/requirements.json", "w") as f:
        if isinstance(state["requirements"], dict):
            json.dump(state["requirements"], f, indent=2)
        else:
            f.write(state["requirements"])
    
    print("Requirements gathered and processed successfully.")
    return state 