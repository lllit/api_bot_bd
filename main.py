from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from utils.security import create_access_token, get_current_user
from utils.calendar_airbnb import download_calendar, arriendo_json

import json
import os
from typing import Any
from llm import human_query_to_sql, human_query_airbnb
from database import query
from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel

from dotenv import load_dotenv

from contextlib import asynccontextmanager

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta antes de que la aplicación comience a recibir solicitudes
    #await download_calendar()
    await arriendo_json()
    yield
    # Código que se ejecuta después de que la aplicación haya terminado de manejar solicitudes



#app = FastAPI(servers=[{"url": BACKEND_SERVER}])
app = FastAPI(lifespan=lifespan)

USERNAME_API = os.getenv("USER_API")
PASSWORD_API = os.getenv("PASSWORD_API") 


class PostHumanQueryPayload(BaseModel):
    human_query: str


class PostHumanQueryResponse(BaseModel):
    result: list


class Token(BaseModel):
    access_token: str
    token_type: str




@app.get("/")
def saludo():
    return {"Bienvenido a la api": "Matias"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Aquí deberías validar el usuario y la contraseña
    # Este es un ejemplo simple que acepta cualquier usuario y contraseña
    if form_data.username != USERNAME_API or form_data.password != PASSWORD_API:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    path="/human_query",
    name="Human Query",
    operation_id="post_human_query",
    description="Gets a natural language query, internally transforms it to a SQL query, queries the database, and returns the result."
)
async def human_query(payload: PostHumanQueryPayload, current_user: str = Depends(get_current_user)) -> dict[str, str]:
    
    try:
        # Transforma la pregunta a sentencia SQL
        sql_query = await human_query_to_sql(payload.human_query)

        if not sql_query:
            return {"error": "Falló la generación de la consulta SQL"}
    

        result_dict = json.loads(sql_query)

        print(f"Result: {result_dict['sql_query']}")


        # Hace la consulta a la base de datos
        result = await query(result_dict['sql_query'])

        print("Result de supabase: ",result)



        # Transforma la respuesta SQL a un formato más humano
        answer = await build_answer(result, payload.human_query)
        
        if not answer:
            return {"error": "Falló la generación de la respuesta"}


        
        
        # Crear el payload para enviar a la API
        payload_dict = {
            "message": answer
        }

        print("Payload dict: ",payload_dict)

        return payload_dict
    
    except Exception as e:
        print("Error al procesar respuesta: ",e)

        payload_dict = {
            "message": "Vuelve a preguntar"
        }
        return payload_dict

    
#--------------- AIRBNB SECTION ----------------------------------

@app.post(
    path="/human_response_airbnb",
    name="Human Query Airbnb",
    operation_id="post_human_query_airbnb",
    description="It obtains a natural language query, reads the schema brought to it, and returns in natural language."
)
async def human_response_airbnb(payload: PostHumanQueryPayload, current_user: str = Depends(get_current_user)) -> dict[str, str]:
    try:
        # Transforma la pregunta a respuesta
        respuesta_llm = await human_query_airbnb(payload.human_query)
        
        # Asegúrate de que respuesta_llm sea una cadena
        if not isinstance(respuesta_llm, str):
            respuesta_llm = str(respuesta_llm)

        # Crear el payload para enviar a la API
        payload_dict = {
            "message": respuesta_llm
        }

        return payload_dict

    except Exception as e:
        print("Error al procesar respuesta: ",e)

        payload_dict = {
            "message": "Vuelve a preguntar"
        }

        print({"message": f"Error: {str(e)}"})


        return payload_dict


@app.get(
    path="/get_data_airbnb",
    name="Get Data Airbnb",
    description="Returns the data from the Airbnb JSON file."    
)
def get_data_airbnb():

    # Ruta al archivo JSON
    json_path = Path("temp_calendar/arriendos.json")

    # Verifica si el archivo existe
    if not json_path.exists():
        return {"error": "El archivo JSON no existe."}

    # Lee el archivo JSON
    with json_path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)


    return data














async def build_answer(result: list[dict[str, Any]], human_query: str) -> str | None:

    from utils.client_llm import cliente_llm

    cliente = cliente_llm()

    system_message = f"""
    Given a user's question and the answer in SQL rows of the database from which the user wants to get the answer,
    write an answer to the user's question.

    I want you to return an answer in human language

    
    If the user asks to delete something (whatever) always ask if you are sure to do this operation.

    You have to pass the response from the supabase database to a human understandable response.    

    <user_question> 
    {human_query}
    </user_question>
    <sql_response>
    {result} 
    </sql_response>
    """

#    "content": f"Esta es la pregunta principal: {human_query}, tienes que creame una respuesta en base a esa pregunta, solo responde en español y basándote en la respuesta SQL proporcionada. Respuesta SQL: {result}, Quiero que en el caso de que generes una tabla lo hagas en markdown, si no es una tabla solo dame texto normal. Trata de solo devolver la respuesta a la pregunta principal, sin ser tan rebundante.", 

    response_llm = cliente.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"Vas a responder en lenguaje humano y responder a la pregunta del usuario basado en la respuesta SQL proporcionada. {system_message}",
            },
            {
                "role": "user",
                "content": f"Esta es la pregunta principal: {human_query}, tienes que crearme una respuesta en base a esa pregunta, solo responde en español y basándote en la respuesta SQL proporcionada. Respuesta SQL: {result}. Quiero que en el caso de que generes una tabla lo hagas en Markdown, si no es una tabla solo dame texto normal. Trata de solo devolver la respuesta a la pregunta principal, sin ser tan redundante. Asegúrate de usar saltos de línea en lugar de etiquetas <br> para el formato de Markdown.",
            }
            
        ],
        model="llama3-8b-8192",
    )

    response = response_llm.choices[0].message.content

    return response





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=9000)