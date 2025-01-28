import re
from unidecode import unidecode
import json
import pymupdf
import os


def clean_mapudungun(text):
    # Normaliza acentos y caracteres especiales
    text = unidecode(text).lower()
    # Elimina números/caracteres extraños (personaliza según tus PDFs)
    return re.sub(r'[^a-zñü\s]', '', text)


def pdf_to_json(pdf_path):
    # Usa PyMuPDF para extraer texto con coordenadas
    doc = pymupdf.open(pdf_path)
    structured_data = []
    all_text = ""

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        texto = clean_mapudungun(span["text"])
                        #print(span["text"])
                        # Aquí lógica para identificar palabras mapudungun-español
                        # Ejemplo básico (adaptar a tu estructura de PDF):
                        #print(texto)
                        # Acumula todo el texto en una sola cadena
                        all_text += texto + " "
    
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]
    #print(file_name)
    # Estructura final con una sola clave "Data"
    structured_data = {file_name: all_text.strip()}

    return structured_data


# Lista de archivos PDF
pdf_files = ["data/Diccionario_mapudungun.pdf", "data/Diccionario-mapudungun-espanol-espanol-mapudungun.pdf"]


#data = pdf_to_json("data/Diccionario_mapudungun.pdf")

# Diccionario para almacenar todos los datos
all_data = []

for pdf_file in pdf_files:
    data = pdf_to_json(pdf_file)
    all_data.append(data)





# Guardar los datos en un archivo JSON
with open("json_data/mapuche_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("Datos guardados correctamente en json_data/mapuche_data.json")


