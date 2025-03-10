from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config import get_groq_llm
from flask import Flask, request, jsonify
import time


app = Flask(__name__)
# Temporary storage to keep track of user decisions
# Important: This is a temporary storage. It will be replaced with a database in the future.
user_review_store = {} 


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
    
    state["review_feedback"] = feedback
    state["review_status"] = "Pending User Approval"
    user_review_store[state["user_stories"]] = "Pending"
    
    return wait_for_user_approval(state)


def wait_for_user_approval(state):
    """
    Waits until the user provides approval via API.
    This function periodically checks for user decision before proceeding.
    """
    user_story_key = state["user_stories"]
    while user_review_store.get(user_story_key) == "Pending":
        print("Waiting for user approval...")
        time.sleep(5)  # Polling every 5 seconds
    
    return user_approve_review(state, user_review_store[user_story_key])

@app.route('/review-feedback', methods=['POST'])
def api_wait_for_approval():
    data = request.json
    review_status = data.get('review_status')
    if review_status not in  ["Approved", "Needs Revision"]:
         return jsonify({"error": "Invalid status. Choose 'Approved' or 'Needs Revision'."}), 400
    
    return jsonify(user_approve_review(data, review_status))



def user_approve_review(state, user_decision):
    if user_decision == "Approved":
        state["review_status"] = "Approved"
    else:
        state["review_status"] = "Needs Revision"
    return state







def request_revised_user_stories(state):
    """
    Function to request revised user stories when the review fails.
    In a real-world case, this would be handled via an API or UI interaction.
    """
    print("User stories need revision. Waiting for updated user stories...")
    state["review_status"] = "Waiting for Revision"
    return state


# it will run on port 5000 by default
if __name__ == '__main__':
    app.run(debug=True, port=5000)

