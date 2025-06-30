from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq  # NEW import
from dotenv import load_dotenv
import os
from news_utils import get_news_articles, summarize_articles

# Load API key from .env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM
llm = ChatGroq(
    api_key=groq_api_key,
    model_name="llama3-8b-8192",  # or llama3-70b-8192, llama3-8b-8192 # Change the model
    temperature=0.7,
    max_tokens=512
)

# Prompt Template
template = """
        You are a smart AI financial assistant. Given the following query, 
        return a concise and insightful summary using relavant information.
        
        Query : {query}
        Summaries : {summaries}
        """

prompt = PromptTemplate.from_template(
    "Based on the user's query: {query}\nand the following news summaries:\n{summaries}\n\nProvide a concise answer."
)

# Chain: Prompt → Model → Text
llm_chain = prompt | llm | StrOutputParser()

def get_summary(query):
    articles = get_news_articles(query)
    summaries = summarize_articles(articles)
    return summaries,articles

"""
- Loads your OpenAI API key
- Initilizes a basic propt and LLM chain using LangChain
- prepares your tool to take a query and return summary
"""

# if __name__ == "__main__":
#     responce = llm_chain.invoke({"query" : "Latest news about Apple stock"})
#     print(f"AI Summary: {responce}")