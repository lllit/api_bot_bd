from groq import Groq
import os

def cliente_llm():

    client = Groq(
        # This is the default and can be omitted
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    
    return client