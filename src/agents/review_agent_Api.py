from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from flask import Flask, request, jsonify
import time
import sys
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm

app = Flask(__name__)
user_review_store = {} 
revised_stories_store = {}

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
    decision = user_review_store[user_story_key]
    if decision == "Needs Revision":
        return request_revised_user_stories(state)
    return user_approve_review(state, decision)


@app.route('/review-feedback', methods=['POST'])
def api_wait_for_approval():
    data = request.json
    review_status = data.get('review_status')
    if review_status not in  ["Approved", "Needs Revision"]:
         return jsonify({"error": "Invalid status. Choose 'Approved' or 'Needs Revision'."}), 400
    user_review_store[data["user_stories"]] = review_status
    return jsonify({"message": "Review decision recorded"})


@app.route("/submit-revised-stories", methods=["POST"])
def api_submit_revised_stories():
    data = request.json
    original_story = data.get("original_story")
    revised_story = data.get("revised_story")
    if not original_story or not revised_story:
        return jsonify({"error": "Both 'original_story' and 'revised_story' are required."}), 400
    revised_stories_store[original_story] = revised_story
    user_review_store[original_story] = "Pending"
    return jsonify({"message": "Revised story submitted. Review will be retried."})


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
    
    user_story_key = state["user_stories"]
    while user_story_key not in revised_stories_store:
        time.sleep(5)  # Polling until the revised story is submitted
    state["user_stories"] = revised_stories_store[user_story_key]
    del revised_stories_store[user_story_key]
    return review_user_stories(state)  # Retry review process


# it will run on port 5000 by default
if __name__ == '__main__':
    app.run(debug=True, port=5000)

