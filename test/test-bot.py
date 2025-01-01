import ollama

def send_whatsapp_message_test():
    # Configura tu modelo Ollama Llama 3

    # Define el mensaje que quieres enviar
    prompt = "Me puedes generar una respuesta en json?"

    try:
        # Genera el mensaje usando el modelo Llama 3
        generated_message = ollama.generate(model="llama3.1:8b",prompt=prompt)
        #print(generated_message)  # Imprime la respuesta completa para depuración

        response = generated_message['response']
        print(response)
    except Exception as e:
        response = f"Error: {str(e)}"

    return response

send_whatsapp_message_test()