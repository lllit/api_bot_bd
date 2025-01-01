import requests

# URL de tu API
url = "http://127.0.0.1:8000/human_query"

# Datos que quieres enviar a tu API


data = {
    "human_query": "¿Cuál es la capital de Francia?"
}

try:
    # Enviar la solicitud POST
    response = requests.post(url, json=data)
    
    # Verificar el estado de la respuesta
    if response.status_code == 200:
        print("Respuesta de la API:", response.json())
    else:
        print("Error al comunicarse con la API:", response.status_code, response.text)


except requests.exceptions.RequestException as e:
    print("Error al intentar conectar con la API:", e)