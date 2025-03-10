from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config import get_groq_llm

def get_review_prompt():
    return PromptTemplate(
        input_variables=["user_stories"],
        template="""
        Review the following user stories:
        "{user_stories}"
        Provide feedback:
        - Identify any missing details
        - Suggest improvements
        - Ensure clarity and completeness
        If the user stories meet the required criteria, respond with 'Approved'.
        Otherwise, suggest revisions and mark as 'Needs Revision'.
        """
    )

def review_user_stories(state):
    review_chain = LLMChain(llm=get_groq_llm(), prompt=get_review_prompt())
    feedback = review_chain.run(user_stories=state["user_stories"])
    
    if "Approved" in feedback:
        state["review_status"] = "Approved"
    else:
        state["review_status"] = "Needs Revision"
        state["review_feedback"] = feedback
    return state

def user_approve_review(state, user_decision):
    if user_decision == "Approve":
        state["review_status"] = "Approved"
    else:
        state["review_status"] = "Needs Revision"
    return state


def wait_for_user_approval(state):
    """
    Function to simulate waiting for user approval.
    In a real system, this would be replaced with an API or UI interaction.
    """
    print("Review Feedback", state["review_"])
    user_decision = input("Enter 'Approved' or 'Needs Revision': ")
    return user_approve_review(state, user_decision)




