from langchain.llms import OpenAI, OpenAIEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import Groq
from langsmith import LangSmithClient
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq # type: ignore

load_dotenv()  

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")


# Initialize LLM
model = ChatGroq( model="llama3-8b-8192", temperature=0, api_key=os.getenv("GROQ_API_KEY"))


## Embeddings
def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")

## LLM OpenAI
def get_llm():
    return OpenAI(model="gpt-4o-mini")

## LLM Groq
def get_groq_llm():
    return model

## LangSmith Client
def get_langsmith_client():
    return LangSmithClient(api_key=LANGSMITH_API_KEY, endpoint=LANGSMITH_ENDPOINT)


