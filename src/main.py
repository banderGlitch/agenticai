# from flask import Flask, request, jsonify
# from langgraph.graph import StateGraph, END
# from agents.requirement_agent import extract_user_stories
# from agents.review_agent import review_user_stories
# from agents.review_agent_Api import wait_for_user_approval, request_revised_user_stories, user_approve_review


# graph = StateGraph()
# ## add nodes
# graph.add_node("requirement_agent", extract_user_stories)
# graph.add_node("review_agent", review_user_stories)
# graph.add_node("approval_agent", wait_for_user_approval)
# graph.add_node("request_revised_user_stories", request_revised_user_stories)
# graph.add_node("user_approve_review", user_approve_review)

# ## add edges
# graph.add_edge("requirement_agent", "review_agent")
# graph.add_edge("review_agent", "approval_agent")





# app = Flask(__name__)


