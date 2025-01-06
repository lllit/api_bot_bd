# Scraping Airbnb
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


# Configurar opciones de Brave
options = Options()
options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"  # Cambia esto a la ruta de tu navegador Brave
options.add_argument("--user-data-dir=C:/Users/litio/AppData/Local/BraveSoftware/Brave-Browser/User Data/Default")  # Ruta al perfil de usuario de Brave
options.add_argument("--profile-directory=Default")  # Nombre del directorio del perfil (por defecto es "Default")
# options.add_argument("--headless")  # Ejecutar en modo headless (sin interfaz gráfica)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--remote-debugging-port=9222")  # Añadir puerto de depuración remota

# Inicializar el WebDriver para Brave
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


url = "https://www.airbnb.cl/hosting/reservations/details/HMXBNB5YNE?_set_bev_on_new_domain=1729615060_EAZDUwYTU2NDg5OG"

# Navegar a la página
driver.get(url)

# Esperar a que la página se cargue completamente
time.sleep(5) 

# Obtener el contenido de la página
page_content = driver.page_source


# Analizar el contenido HTML de la página
soup = BeautifulSoup(page_content, "html.parser")

# Ejemplo: Obtener el título de la página
title = soup.title.string
print(f"Título de la página: {title}")

# Ejemplo: Obtener todos los enlaces en la página
links = soup.find_all("a")
for link in links:
    print(link.get("href"))

# Ejemplo: Obtener un elemento específico por su clase
# Cambia 'class-name' por la clase del elemento que quieres obtener
element = soup.find(class_="class-name")
if element:
    print(f"Elemento encontrado: {element.text}")

# Cerrar el navegador
driver.quit()