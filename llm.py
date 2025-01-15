from database import get_schema
from utils.client_llm import cliente_llm

import httpx
import ollama
from datetime import datetime
import pytz

cliente = cliente_llm()

# Define la zona horaria de Chile
chile_tz = pytz.timezone('America/Santiago')

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



    now = datetime.now(chile_tz)

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
    Eres un secretario en Chile encargado de gestionar arrendamientos de cabañas. Debes responder de manera concreta y formal, basándote en el esquema proporcionado.

    - El esquema es un JSON por ende tienes que leer este JSON y entregar una respuesta coherente

    - El JSON contiene las noches arrendadas. Se te hara una pregunta en lenguaje natural y tienes que analizar el esquema, en base al esquema tienes dar una respuesta Coherente

    - Tienes que entender que el esquema tiene algo como: 
        Ejemplo:
        "Fecha Inicio": "17/1/2025", "Fecha Fin": "19/1/2025", el 17, 18, 19 estan arrendados, y se tendran que ir el 19 antes de las 11
        Asi va a pasar con todas las fechas de inicio y de fin, seran diferentes los dias, tienes que analizar esto.
        Si esque te preguntan algun dia entremedio de la fecha inicio y fecha de fin 
            - por ejemplo el 18 de enero este dia esta arrendado ya que esta entre las fechas de inicio y de fin

            
    - Hay "Fecha Inicio" y "Fecha Fin", para sacar los dias que estan arrendados, tienes que restar la fecha de inicio con la fecha de fin 
    - "Días de arriendo" son el total de dias que se estan arrendados entre la Fecha Inicio con la Fecha Fin
    - Cuando te pregunten ¿Que dias tienes arrendados? tienes que dar todos las fechas, incluyendo Fechas de inicio con fecha de fin


    - Recibirás un archivo JSON con las noches arrendados de una cabaña. Tu tarea es:
    - Leer el esquema en forma de JSON: {esquema} y responder en base a este.
    - Generar una respuesta directa a la pregunta utilizando la información del esquema.
    - Hacer cálculos de fechas según "Fecha Inicio" y "Fecha Fin" (quiero que tengas en cuenta el check-in y check-out).
    - Responder en pesos chilenos.
    - Si te preguntan por noches disponibles, usa la fecha actual: "{dia}/{mes}/{año}" para verificar disponibilidad.
    - Recuerda que el check-in es a las 14:00 y el check-out es a las 12:00.
    

    Responde siempre en español, de manera concisa y basada en el esquema.

    El esquema incluye "Ingresos", que es el valor pagado por el arriendo total.
    El esquema trae todos los dias que estan arrendados.


    Esquema:
    <schema>
    {esquema}
    </schema>

    Información adicional de la cabaña:

    Cuenta con:
    - 2 Dormitorios
    - 1 Cama Matrimonial
    - 2 Cama de media plaza
    - 1 Sillon Cama
    - TV por cable
    - Wifi
    - Calefacción toyotomi y estufa a leña
    - 1 baño
    - Cocina equipada completa

    Comodidades:
    - Agua caliente
    - Calefacción
    - Cocina
    - Estacionamiento gratuito en la calle y en las instalaciones
    - Ganchos para la ropa
    - Horno
    - Lavadora
    - Lavavajillas
    - Microondas
    - Plancha
    - Platos y cubiertos
    - Refrigerador
    - Servicios imprescindibles (toallas, sábanas, jabón y papel higiénico)
    - TV
    - Utensilios básicos para cocinar (ollas, sartenes, aceite, sal y pimienta)
    - Wifi disponible en todo el alojamiento

    Dirección:
    - Presidente Patricio Alwyn Azócar 701, Puerto Varas, Los Lagos
    - Link de google maps: https://www.google.com/maps/place/Aylwin+Azocar+-+Pdte.+Patricio+Alwyn+Az%C3%B3car+701,+Puerto+Varas,+Los+Lagos/@-41.3131248,-72.9944937,59m/data=!3m1!1e3!4m6!3m5!1s0x961820d4bf672cdf:0x9a3b37a94c43d656!8m2!3d-41.3130474!4d-72.9945193!16s%2Fg%2F11tf45g1vf?hl=es&entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D

    Reglas de la casa:
    - No se admiten mascotas
    - No se admiten eventos con música fuerte después de las 23:00
    - No está permitido fumar cigarrillos
    - Se permite la fotografía y la filmación comerciales

    Número de personas: 4

    Horas de check-in y check-out:
    - Llegada: de 14:00 a 00:00
    - Salida antes de las 12:00 PM

    
    
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
                "content": f"Tienes que responder esta pregunta: {user_message}, quiero respuestas directas, sin tanto texto, y siempre en español",
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