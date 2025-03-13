from langchain_core.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
import json
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_user_story_prompt():
    return PromptTemplate(
        input_variables=["requirements", "revision_feedback"],
        template="""
        You are a product manager skilled in creating user stories. Based on the following requirements,
        generate comprehensive user stories in the format: "As a [user role], I want [goal], so that [benefit]."
        
        Requirements:
        {requirements}
        
        {revision_feedback}
        
        For each user story:
        1. Clearly identify the user role
        2. Specify what they want to accomplish
        3. Explain the benefit or value they'll receive
        4. Add acceptance criteria (how we'll know when the story is complete)
        
        Group stories by user role and prioritize them (High, Medium, Low).
        """
    )

def generate_user_stories(state, revision=False):
    """
    Generate user stories based on requirements
    """
    # Prepare requirements input
    if isinstance(state["requirements"], dict):
        requirements_text = json.dumps(state["requirements"], indent=2)
    else:
        requirements_text = state["requirements"]
    
    # Prepare revision feedback if applicable
    revision_feedback = ""
    if revision and "review_feedback" in state:
        revision_feedback = f"Revision Feedback: {state['review_feedback']}\nPlease address this feedback in your revised user stories."
    
    # Generate user stories with LLM
    user_story_chain = LLMChain(llm=get_groq_llm(), prompt=get_user_story_prompt())
    user_stories = user_story_chain.run(
        requirements=requirements_text,
        revision_feedback=revision_feedback
    )
    
    state["user_stories"] = user_stories
    
    # Save user stories to file
    os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)
    with open(f"{PROJECT_CONFIG['output_dir']}/user_stories.md", "w") as f:
        f.write(user_stories)
    
    print("User stories generated successfully.")
    return state 