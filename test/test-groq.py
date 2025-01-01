import os

from groq import Groq

client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. Please respond in JSON format. Make sure your response is a valid JSON object."
        },
        {
            "role": "user",
            "content": "Me puedes responder en español?",
        }
    ],
    response_format={ "type": "json_object" },
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)