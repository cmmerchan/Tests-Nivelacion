import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from resources.authenticator import Authenticator
from resources.functions import Functions
from resources.moodle_test import MoodleTest

from models.user_credentials import User
from models.question import Question
from utils.timeouts import Timeouts
from db.mongodb import MongoDB
import chromedriver_autoinstaller
import sys

import shutil
import tempfile
import os

import time
# import pyautogui


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

class AltissiaWebDriver:
    def __init__(self, url:str,db:MongoDB,index:int):
        self.index = index  # Index for window grid positioning
        self.driver, self.temp_dir = self.launch_browser()
        self.url = url
        
        # self.authenticator = Authenticator(self.driver,user,db)
        self.functions = Functions(self.driver)
        self.moodle_test = MoodleTest(self.driver,db) # Placeholder for EnglishTest instance
        self.db = db
        

    def launch_browser(self)->tuple[uc.Chrome, str]: #TODO: Manage chromedriver version mistmached and update it if necessary 
        original_driver_path = chromedriver_autoinstaller.install()

        # Crear carpeta temporal para evitar conflictos entre procesos
        temp_dir = tempfile.mkdtemp(prefix="uc_chrome_")

        # Nombre del ejecutable
        driver_filename = "chromedriver.exe" if sys.platform.startswith('win') else "chromedriver"
        local_driver_path = os.path.join(temp_dir, driver_filename)

        try:
            shutil.copyfile(original_driver_path, local_driver_path)
        except shutil.SameFileError:
            pass  # Ya está copiado
        except Exception as e:
            sys.exit(1)
        
        ancho_ventana, alto_ventana, x, y = self.set_window_grid(self.index)

        options = uc.ChromeOptions() # Configurar opciones de Chrome
        options.add_argument("--disable-blink-features=AutomationControlled")  # Evita detección de bots
        options.add_argument("--disable-logging") 
        options.add_argument("--no-first-run") 
        options.add_argument("--no-default-browser-check") 
        
        options.add_argument("--start-maximized")  # Maximiza al inicio

        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        # options.add_argument("--mute-audio")  # <-- Esto silencia el audio del navegador
        prefs = {
        "profile.default_content_setting_values.media_stream_mic": 2,  # 2 = bloquear micrófono
        "profile.default_content_setting_values.media_stream_camera": 2,  # por si acaso también cámara
        "profile.default_content_setting_values.geolocation": 2,  # por si piden ubicación
        }
        options.add_experimental_option("prefs", prefs)

        try:    
            driver = uc.Chrome(driver_executable_path=local_driver_path, options=options, use_subprocess=True)
            # driver.set_window_size(ancho_ventana, alto_ventana)
            # driver.set_window_position(x, y)

            return driver,temp_dir
        except Exception as e:
            raise Exception(f"Error launching Chrome")

    def ensure_chromedriver_installed(self):
        chromedriver_autoinstaller.install()  # Instala el controlador de Chrome automáticamente si no está presente

    def cleanup(self):
        #Cerrar el navegador y eliminar carpeta temporal
        if self.driver:
            self.driver.quit()
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def set_window_grid(self, index):
        # Detectar resolución real de tu pantalla
        if index == 4:
            index =0
        if index == 5:
            index =1
        if index == 6:
            index =2
        if index == 7:
            index =3
        
        ancho_pantalla = 1920
        alto_pantalla = 1080 - 40

        # Tamaño de cada ventana (la mitad de la pantalla)
        ancho_ventana = ancho_pantalla // 2
        alto_ventana = alto_pantalla // 2
        fila = index // 2       # 0 o 1
        columna = index % 2     # 0 o 1
        x = columna * ancho_ventana
        y = fila * alto_ventana

        return ancho_ventana, alto_ventana, x, y

    def run(self):
        self.driver.get(self.url)
        time.sleep(3)  # Esperar a que la página cargue
        self.navigate_to_prueba()

    def navigate_to_prueba(self):
        self.moodle_test.explore_moodle()  # Iniciar la prueba de inglés

    