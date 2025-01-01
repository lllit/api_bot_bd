from database import get_schema
from utils.client_llm import cliente_llm

import ollama
import asyncio
import json

cliente = cliente_llm()


async def human_query_to_sql(human_query: str):

    # Obtenemos el esquema de la base de datos
    database_schema = get_schema()

    system_message = f"""
    Given the following schema, write a SQL query that works on supabase and retrieves the requested information. 
    I expect you to return the SQL query inside a JSON structure with the key “sql_query”. 
    I will give you an example on which you have to base your query
    <example>{{
        "sql_query": "SELECT COUNT(*) AS total_usuarios FROM usuarios;"
        "original_query": "how many users I have registered?"
    }}
    </example>
    This is the schema of my database in supabase:
    <schema>
    {database_schema}
    </schema>
    """
    user_message = human_query


    # generated_message = ollama.generate(
    #     model="qwen2.5-coder",
    #     prompt=user_message, 
    #     format="json",
    #     system=system_message,
    #     template=f"""
    #     This is the schema of my database in supabase
    #     <example>{{
    #         "sql_query": "SELECT * FROM usuarios ORDER BY id ASC LIMIT 1;"
    #         "original_query": "I want to find the first user that registered in my application."
    #     }}
    #     </example>
    #     <schema>
    #     {database_schema}
    #     </schema>
    #     """
    #     )

    generated_message = cliente.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message,
            }
        ],
        response_format={ "type": "json_object" },
        model="llama3-8b-8192",
    )

    print("Response: ", generated_message.choices[0].message.content)
    # Imprime la respuesta completa para depuración
    #print("Generated Message:", generated_message["response"])

    # Verifica si la respuesta contiene la clave 'response'
    # if 'response' not in generated_message:
    #     return {"error": "La respuesta no contiene la clave 'response'"}

    response = generated_message.choices[0].message.content

    
    print("Response ", response)

    return response


async def response_to_llm(reponse_llm: str):
    # Obtenemos el esquema de la base de datos
    database_schema = get_schema()


    system_message = f"""
    I have my database in supabase and I want you to build me a query for this database.
    Given the following schema, write a SQL query that works for my supabase database and is consistent with the table schema I have in my database.
    Return the SQL query within a JSON structure with the key “sql_query”.
    <example>{{
        "sql_query": "SELECT * FROM usuarios ORDER BY id ASC LIMIT 1;"
        "original_query": "I want to find the first user that registered in my application."
    }}
    </example>
    <schema>
    {database_schema}
    </schema>
    """

    user_message = reponse_llm

    generated_message = ollama.generate(
        model="qwen2.5-coder:latest",
        prompt=user_message, 
        format="json",
        system=system_message,
        template=f"""
            <example>{{
            "sql_query": "SELECT * FROM usuarios ORDER BY id ASC LIMIT 1;"
            "original_query": "I want to find the first user that registered in my application."
            }}
            </example>
        <schema>
        {database_schema}
        </schema>
        """
        )


    # Imprime la respuesta completa para depuración
    print("Generated Message:", generated_message)

    # Verifica si la respuesta contiene la clave 'response'
    if 'response' not in generated_message:
        return {"error": "La respuesta no contiene la clave 'response'"}

    response = generated_message['response']

    
    print("Response ", response)

    return response





async def test_response():
    response = await human_query_to_sql(human_query="Que tablas tengo en mi base de datos")

    return response





def send_whatsapp_message_test():
    # Configura tu modelo Ollama Llama 3

    # Define el mensaje que quieres enviar
    prompt = "Me puedes generar una respuesta en json?"

    try:

        system_message = f"""
        Given the following schema, write a SQL query that retrieves the requested information. 
        Return the SQL query inside a JSON structure with the key "sql_query".
        <example>{{
            "sql_query": "SELECT * FROM users WHERE age > 18;"
            "original_query": "Show me all users older than 18 years old."
        }}
        </example>
        <schema>
        
        </schema>
        """
        user_message = prompt

        generated_message = ollama.generate(
            model="llama3.1:8b",
            prompt=user_message, 
            format="json",
            system=system_message,
            template=f"""
            <example>{{
                "sql_query": "SELECT * FROM users WHERE age > 18;"
                "original_query": "Show me all users older than 18 years old."
            }}
            </example>
            <schema>
            </schema>
            """
            )

        response = generated_message['response']
        print(response)

        # Genera el mensaje usando el modelo Llama 3
        #generated_message = ollama.generate(model="llama3.1:8b",prompt=prompt)
        #print(generated_message)  # Imprime la respuesta completa para depuración


    except Exception as e:
        response = f"Error: {str(e)}"

    return response

#send_whatsapp_message_test()