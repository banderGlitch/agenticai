from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_design_prompt():
    return PromptTemplate(
        input_variables=["user_stories", "project_name"],
        template="""
        You are a software architect. Based on the following approved user stories,
        create comprehensive design documents for the project named "{project_name}".
        
        User Stories:
        {user_stories}
        
        Please provide:
        
        # Functional Design
        1. System Overview
        2. User Interfaces (describe each screen/page)
        3. Data Models (entities and relationships)
        4. Business Logic and Workflows
        5. Integration Points (APIs, external systems)
        
        # Technical Design
        1. Architecture Overview (include a diagram description)
        2. Technology Stack
        3. Component Design
        4. Database Schema
        5. API Specifications
        6. Security Considerations
        7. Performance Considerations
        8. Deployment Strategy
        
        Be specific and detailed in your design.
        """
    )

def get_design_review_prompt():
    return PromptTemplate(
        input_variables=["design_documents"],
        template="""
        Review the following design documents:
        
        {design_documents}
        
        Provide feedback on:
        1. Completeness - Does it cover all requirements?
        2. Clarity - Is the design clear and understandable?
        3. Feasibility - Is the design technically feasible?
        4. Scalability - Will the design scale as needed?
        5. Security - Are security concerns addressed?
        6. Maintainability - Is the design maintainable?
        
        If the design meets all criteria, respond with 'Approved'.
        Otherwise, suggest specific improvements and mark as 'Needs Revision'.
        """
    )

def create_design_documents(state):
    """
    Create functional and technical design documents based on approved user stories
    """
    design_chain = LLMChain(llm=get_groq_llm(), prompt=get_design_prompt())
    design_documents = design_chain.run(
        user_stories=state["user_stories"],
        project_name=state["project_name"]
    )
    
    state["design_documents"] = design_documents
    
    # Save design documents to file
    os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)
    with open(f"{PROJECT_CONFIG['output_dir']}/design_documents.md", "w") as f:
        f.write(design_documents)
    
    print("Design documents created successfully.")
    return state

def review_design(state):
    """
    Review the design documents
    """
    review_chain = LLMChain(llm=get_groq_llm(), prompt=get_design_review_prompt())
    feedback = review_chain.run(design_documents=state["design_documents"])
    
    state["design_review_feedback"] = feedback
    
    if "Approved" in feedback:
        state["design_review_status"] = "Approved"
        print("Design review: Approved")
    else:
        state["design_review_status"] = "Needs Revision"
        print("Design review: Needs Revision")
        print("Feedback:", feedback)
        
        # Ask user for decision
        user_decision = input("Enter 'Approved' to proceed anyway, or 'Revise' to update the design: ")
        if user_decision.lower() == "revise":
            # Implement logic to revise design
            print("Revising design based on feedback...")
            # This would call a function to revise the design
            # For now, we'll just update the status
            state["design_review_status"] = "Needs Revision"
        else:
            state["design_review_status"] = "Approved"
    
    return state
