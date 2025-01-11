from database import get_schema
from utils.client_llm import cliente_llm

import httpx
import ollama
from datetime import datetime

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


# --------- AIRBNB SECTION -----------------

async def human_query_airbnb(human_query: str):

    now = datetime.now()

    # Obtener el día, mes y año
    dia = now.day
    mes = now.month
    año = now.year

    # Obtener esquema
    async with httpx.AsyncClient() as client:
        response = await client.get("https://apibotbd.vercel.app/get_data_airbnb")
        response.raise_for_status()  # Lanza una excepción si la solicitud falla
        esquema = response.json()
    
    system_message = f"""
    Eres un secretario en Chile encargado de gestionar arrendamientos de cabañas. 
    Debes responder de manera concreta y formal, basándote en el esquema que te proporciono a continuación.

    Esta cabaña solo esta disponible en los meses de Enero y Febrero

    Valor de la cabaña por noche es: $60000 Pesos Chilenos

    El Json contiene solo las noches que estan arrendados, tendras que hacer calculos internos y solo dar la respuesta concreta
    Hay "Fecha Inicio" y "Fecha Fin", tambien tiene un recuento de dias "Días de arriendo", estos son los dias totales de las fechas de inicio con las fecha de fin

    Recibirás un archivo JSON con los días arrendados de una cabaña. 
    Tu tarea es: 
    - Leer el Esquema en forma de Json: {esquema} y en base a este esquema responder
    - generar una respuesta directa a la pregunta que se te haga, utilizando la información del esquema.
    - Hacer calculos de fechas segun "Fecha Inicio" y "Fecha Fin"
    - Responder coherentemente en pesos chilenos
    - Si te preguntan por temas de que noches hay disponible, basate en la fecha actual: "Día: {dia}, Mes: {mes}, Año: {año}" y en base a esta fecha ve la disponibilidad  
    - Ten encuenta de que los pasajeros tienes que hacer el checkin a las 14:00 y el checkout es a las 12:00, 

    Recuerda siempre responder en español, en base al esquema tienes que darme respuestas concisas a la pregunta que se te entrega.

    Este es el esquema:
    <schema>
    {esquema}
    </schema>

    Datos necesarios en el caso de que pregunten mas informacion adicional de la cabaña:

    Cuenta con:
    - 2 Dormitorios.
    - TV por cable
    - Wifi
    - calefaccion toyotomi y estufa a leña
    - 1 baño
    - Cocina equipada completa

    Comodidades
        - Agua caliente
        - Calefacción
        - Cocina
        - Los huéspedes pueden cocinar en este espacio
        - Estacionamiento gratuito en la calle
        - Estacionamiento gratuito en las instalaciones
        - Ganchos para la ropa
        - Horno
        - Lavadora
        - Lavavajillas
        - Microondas
        - Plancha
        - Platos y cubiertos
        - Bols, palitos chinos, platos, tazas, etc.
        - Refrigerador
        - Servicios imprescindibles
        - Toallas, sábanas, jabón y papel higiénico
        - TV
        - Utensilios básicos para cocinar
        - Ollas y sartenes, aceite, sal y pimienta
        - Wifi
        - Disponible en todo el alojamiento


    Dirección

    - Presidente Patricio Alwyn Azócar

    Departamento, piso, etc. (si corresponde)

    - 701

    Ciudad / pueblo / municipio

    - Puerto Varas

    Región

    - Regios de los Lagos

    Direccion completa: Aylwin Azocar - Pdte. Patricio Alwyn Azócar 701, Puerto Varas, Los Lagos
    
    UBICACION EXACTA (LINK DE GOOGLE MAPS): https://www.google.com/maps/place/Aylwin+Azocar+-+Pdte.+Patricio+Alwyn+Az%C3%B3car+701,+Puerto+Varas,+Los+Lagos/@-41.3131248,-72.9944937,59m/data=!3m1!1e3!4m6!3m5!1s0x961820d4bf672cdf:0x9a3b37a94c43d656!8m2!3d-41.3130474!4d-72.9945193!16s%2Fg%2F11tf45g1vf?hl=es&entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D

    
    
    ## Reglas de la casa

    - No se admiten mascotas

    - No se admiten eventos con musica fuerte despues de las 23:00


    - No Está permitido fumar cigarrillos.

    
    Se permite la fotografía y la filmación comerciales

    Número de personas: 4


    Horas de check-in y check-out
    Llegada: de 14:00 a 00:00.
    Salida antes de las 12:00 PM.


    
    """

    user_message = human_query

    generated_message = cliente.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": f"Tienes que responder esta pregunta: {user_message}, quiero respuestas directas, sin tanto texto",
            }
        ],
        model="llama3-8b-8192",
    )

    response = generated_message.choices[0].message.content

    
    print("Response ", response)

    return response

    






















# --------- TEST ------------

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