import re
from unidecode import unidecode
import json
import pymupdf
import os
import sys

# Agregar el directorio raíz al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client_llm import cliente_llm





cliente = cliente_llm()




def clean_mapudungun(text):
    # Normaliza acentos y caracteres especiales
    text = unidecode(text).lower()
    # Elimina números/caracteres extraños (personaliza según tus PDFs)
    return re.sub(r'[^a-zñü/s]', '', text)


def pdf_to_json(pdf_path):
    # Usa PyMuPDF para extraer texto con coordenadas
    doc = pymupdf.open(pdf_path)
    all_text = []


    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        texto = clean_mapudungun(span["text"])
                        # Acumula todo el texto en una lista
                        all_text.append(texto + " ")

    combined_text = " ".join(all_text).strip()

    file_name = os.path.splitext(os.path.basename(pdf_path))[0]
    #print(file_name)
    # Estructura final con una sola clave "Data"
    structured_data = {file_name: combined_text}

    return structured_data


# Lista de archivos PDF
pdf_files = ["data/Diccionario_mapudungun.pdf", "data/Diccionario-mapudungun-espanol-espanol-mapudungun.pdf"]


#data = pdf_to_json("data/Diccionario_mapudungun.pdf")



# Diccionario para almacenar todos los datos
all_data = []




for pdf_file in pdf_files:
    data = pdf_to_json(pdf_file)
    all_data.append(data)




if __name__ == "__main__":

    try:
        ruta_final = "D:/LLLIT/Code-W11/PY/api_bot_bd/temp_calendar/mapu/mapu.json"


        # Guardar los datos en un archivo JSON
        with open(ruta_final, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
            print(f"Datos guardados correctamente en {ruta_final}")
    except:
        print("Error")

