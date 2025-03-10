from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config import get_groq_llm
from flask import Flask, request, jsonify


app = Flask(__name__)

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
    
    return state  # Now approved happens in the api

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


if __name__ == '__main__':
    app.run(debug=True, port=5000)

