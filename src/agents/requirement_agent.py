from langchain.chains import LLMChain    ## what is this llmchain?
from langchain_core.prompts import PromptTemplate
from config import get_groq_llm

# requirement prompts
requirement_prompt = PromptTemplate(
    input_variables=["requirements"],
    template="""
    Given the following user requirements:
    "{requirements}"
    Extract structured user stories following this format:
    - Title: [short name]
    - Description: [detailed explanation]
    - Acceptance Criteria: [list key expectations]
    - Priority: [High, Medium, Low]
    """
)

requirement_chain = LLMChain(llm=get_groq_llm(), prompt=requirement_prompt)

def extract_user_stories(state):
    state["user_stories"] = requirement_chain.run(requirements=state["requirements"])
    return state  ## returns the state with the user stories






