from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
# from langsmith import LangSmithClient
from dotenv import load_dotenv

import os
from langchain_community.llms import Groq
from langchain_community.chat_models import ChatGroq

load_dotenv()  

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
# LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")


# Initialize LLM
model = ChatGroq(model="llama3-8b-8192", temperature=0, api_key=os.getenv("GROQ_API_KEY"))


## Embeddings
def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")

## LLM OpenAI
def get_llm():
    return OpenAI(model="gpt-4o-mini")

## LLM Groq
def get_groq_llm():
    """
    Returns a configured Groq LLM instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    return Groq(
        api_key=api_key,
        model_name="llama3-70b-8192"  # You can change this to your preferred model
    )

def get_groq_chat():
    """
    Returns a configured Groq Chat model instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    return ChatGroq(
        api_key=api_key,
        model_name="llama3-70b-8192"  # You can change this to your preferred model
    )

# ## LangSmith Client
# def get_langsmith_client():
#     return LangSmithClient(api_key=LANGSMITH_API_KEY, endpoint=LANGSMITH_ENDPOINT)

# Project configuration
PROJECT_CONFIG = {
    "output_dir": "output",
    "templates_dir": "src/templates",
    "max_tokens": 4096,
    "temperature": 0.7
}

# Ensure output directory exists
os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)


