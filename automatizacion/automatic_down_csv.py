from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from pywinauto.application import Application
from pywinauto import timings
from dotenv import load_dotenv
import os
import shutil

load_dotenv()



USER = os.getenv('CORREO')
PASS = os.getenv('PASS')

# Configurar el navegador Brave
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

options = webdriver.ChromeOptions()
options.binary_location = brave_path
driver = webdriver.Chrome(options=options)


# Navegar a la página de inicio de sesión de Airbnb
driver.get('https://www.airbnb.cl/login')

# Hacer clic en el botón de autenticación con correo electrónico
email_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="social-auth-button-email"]')

time.sleep(5)

email_button.click()

# Esperar a que se abra la ventana de autenticación de Google
time.sleep(5)


# Ingresar el correo electrónico
email_input = driver.find_element(By.ID, 'email-login-email')
email_input.send_keys(USER)

time.sleep(5)
# CLICK
submit_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="signup-login-submit-btn"]')
submit_button.click()

time.sleep(5)

#Pass
pass_input = driver.find_element(By.ID, "email-signup-password")
pass_input.send_keys(PASS)


time.sleep(5)

#CLICK
iniciar_sesion_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="signup-login-submit-btn"]')
iniciar_sesion_button.click()


time.sleep(10)

# Descargar el archivo después de la autenticación
driver.get('https://www.airbnb.cl/api/v2/download_reservations?_format=for_remy&_limit=40&_offset=0&collection_strategy=for_reservations_list&date_max=2025-03-01&date_min=2024-12-31&listing_id=31351779&sort_field=start_date&sort_order=desc&status=accepted%2Crequest%2Ccanceled&page=1&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&currency=CLP&locale=es-XL')

time.sleep(5)

try:

   # Usar pywinauto para interactuar con la ventana de confirmación de ruta
    app = Application(backend="win32").connect(title_re=".*www.airbnb.cl desea guardar.*", timeout=20)
    save_as_dialog = app.window(title_re=".*www.airbnb.cl desea guardar.*")
    save_as_dialog.wait('visible', timeout=20)
    save_as_dialog.child_window(title="Guardar", control_type="Button").wait('enabled', timeout=20).click()
    
except Exception as e:
    print(e)


try:
    # Guardar el archivo descargado
    with open('D:/LLLIT/Code-W11/PY/api_bot_bd/temp_calendar/reservations_all.csv', 'wb') as file:
        file.write(driver.page_source.encode('utf-8'))
except Exception as e:
    print(e)



# Ruta de la carpeta de descargas
downloads_folder = 'C:/Users/litio/Downloads'

# Buscar el archivo .tmp más reciente en la carpeta de descargas
tmp_files = [f for f in os.listdir(downloads_folder) if f.endswith('.tmp')]
latest_tmp_file = max(tmp_files, key=lambda f: os.path.getctime(os.path.join(downloads_folder, f)))

# Ruta completa del archivo .tmp más reciente
tmp_file_path = os.path.join(downloads_folder, latest_tmp_file)

# Nueva ruta y nombre del archivo .csv
csv_file_path = 'D:/LLLIT/Code-W11/PY/api_bot_bd/temp_calendar/reservations_all.csv'

try:
    # Cambiar la extensión y renombrar el archivo
    shutil.move(tmp_file_path, csv_file_path)
    print(f"El archivo ha sido renombrado y movido a {csv_file_path}")
except Exception as e:
    print(e)

driver.quit()