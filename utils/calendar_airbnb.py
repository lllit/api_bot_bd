from fastapi import FastAPI
import icalendar
import requests
from pathlib import Path
import json
import asyncio
import csv


# En el caso de que quiera guardar el esquema en un json
def guardar_json(temp_calendar_dir, arriendos):
    # Guardar los datos en un archivo JSON
    json_path = temp_calendar_dir / "arriendos.json"
    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(arriendos, json_file, ensure_ascii=False, indent=4)

    # Leer y mostrar el contenido del archivo JSON
    with json_path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
        #print(json.dumps(data, ensure_ascii=False, indent=4))



async def download_calendar():
    try:
        # URL del archivo .ics
        url = "https://www.airbnb.cl/calendar/ical/31351779.ics?s=b33143189db89132f106f3939522c5da"


        # Descargar el archivo .ics
        response = requests.get(url)
        ics_content = response.content

        # Crear la carpeta temp_calendar si no existe
        temp_calendar_dir = Path("temp_calendar")
        temp_calendar_dir.mkdir(exist_ok=True)

        # Guardar el archivo .ics en la carpeta temp_calendar
        ics_path = temp_calendar_dir / "listing-31351779.ics"
        ics_path.write_bytes(ics_content)


        #ics_path = Path("listing-31351779.ics")

        with ics_path.open() as f:
            calendar = icalendar.Calendar.from_ical(f.read())

        contador = 1
        dias_arriendo_totales = 0
        arriendos = []

        for event in calendar.walk('VEVENT'):
            if event.get("SUMMARY") == "Airbnb (Not available)":
                break

            dtstart = event.get("DTSTART").dt
            dtend = event.get("DTEND").dt

        
            # Calcular la cantidad de días de arriendo
            dias_arriendo = (dtend - dtstart).days
            
            dias_arriendo_totales += dias_arriendo

            arriendo = {
                "Arriendo N°": contador,
                "Fecha Inicio": str(dtstart),
                "Fecha Fin": str(dtend),
                "Días de arriendo": dias_arriendo
            }
            arriendos.append(arriendo)
            contador += 1

        arriendos.append({"Dias totales arrendados": dias_arriendo_totales})

        # Agregar la data que falta


        # Merge with CSV data
        csv_path = temp_calendar_dir / "reservations_all.csv"

        with csv_path.open() as csv_file:
            csv_reader = csv.DictReader(csv_file)
            csv_list = list(csv_reader)

        

        for json_entry in arriendos:

            if 'Fecha Inicio' in json_entry and 'Fecha Fin' in json_entry:
                for csv_entry in csv_list:
                    if (json_entry['Fecha Inicio'] == csv_entry['Fecha de inicio'].replace(" ", "") and 
                        json_entry['Fecha Fin'] == csv_entry['Hasta'].replace(" ", "")):
                        json_entry.update({
                            "Código de confirmación": csv_entry["Código de confirmación"],
                            "Estado": csv_entry["Estado"],
                            "Nombre del huésped": csv_entry["Nombre del huésped"],
                            "Contacta": csv_entry["Contacta"],
                            "Número de adultos": csv_entry["Número de adultos"],
                            "Número de niños": csv_entry["Número de niños"],
                            "Número de bebés": csv_entry["Número de bebés"],
                            "Número de noches": csv_entry["Número de noches"],
                            "Reservado": csv_entry["Reservado"],
                            "Anuncio": csv_entry["Anuncio"],
                            "Ingresos": csv_entry["Ingresos"]
                        })
        
        guardar_json(temp_calendar_dir, arriendos)

        return arriendos

    except Exception as e:
        print("Error al procesar respuesta: ",e)

        return {"message": str(e)}


async def get_esquema_data():
    try:
        # Ruta al archivo CSV
        csv_path = Path("temp_calendar/reservations_all.csv")

        # Leer los datos del archivo CSV
        with csv_path.open(encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            csv_list = list(csv_reader)

        # Crear la lista de diccionarios con el formato especificado
        arriendos = []
        contador = 1
        dias_totales_arrendados = 0

        for csv_entry in csv_list:
            dias_arriendo = int(csv_entry["Número de noches"])
            dias_totales_arrendados += dias_arriendo

            arriendo = {
                "id": contador,
                "Fecha Inicio": csv_entry["Fecha de inicio"],
                "Fecha Fin": csv_entry["Hasta"],
                "Días de arriendo": dias_arriendo,
                "Código de confirmación": csv_entry["Código de confirmación"],
                "Estado": csv_entry["Estado"],
                "Nombre del huésped": csv_entry["Nombre del huésped"],
                "Contacta": csv_entry["Contacta"],
                "Número de adultos": csv_entry["Número de adultos"],
                "Número de niños": csv_entry["Número de niños"],
                "Número de bebés": csv_entry["Número de bebés"],
                "Número de noches": csv_entry["Número de noches"],
                "Reservado": csv_entry["Reservado"],
                "Anuncio": csv_entry["Anuncio"],
                "Ingresos": csv_entry["Ingresos"]
            }
            arriendos.append(arriendo)
            contador += 1

        arriendos.append({"Dias totales arrendados": dias_totales_arrendados})

        # Guardar los datos en un archivo JSON
        temp_calendar_dir = Path("temp_calendar")
        guardar_json(temp_calendar_dir, arriendos)

        return arriendos

    except Exception as e:
        print("Error al procesar respuesta: ", e)
        return {"message": str(e)}


def arriendo_json():
    return get_esquema_data()




