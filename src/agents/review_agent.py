from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config import get_groq_llm

# review prompts
review_prompt = PromptTemplate(
     input_variables=["user_stories"],
    template="""
    Review the following user stories:
    "{user_stories}"
    Provide feedback:
    - Identify any missing details
    - Suggest improvements
    - Ensure clarity and completeness
    """
)

review_chain = LLMChain(llm=get_groq_llm(), prompt=review_prompt)

def review_user_stories(state):
    state["review"] = review_chain.run(user_stories=state["user_stories"])
    return state ## returns the final a
