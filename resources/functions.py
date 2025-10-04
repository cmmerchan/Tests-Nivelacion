import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import time

from utils.timeouts import Timeouts

class Functions:
    def __init__(self, driver:uc.Chrome):
        self.driver = driver

    def find_grid_elements_ref_by_id(self,grid_ID:str)->list[WebElement]:
        grid = WebDriverWait(self.driver, Timeouts.waitForAResourceToAppear).until(
            EC.presence_of_element_located((By.ID, grid_ID)),
            message=f"Grid element with ID '{grid_ID}' not found in time."
        )
        grid_elements = grid.find_elements(By.CLASS_NAME, "c-kOgFh")
        return grid_elements
    
    def find_grid_elements_ref(self,grid_classname:str)->list[WebElement]:
        grid = WebDriverWait(self.driver, Timeouts.waitForAResourceToAppear).until(
            EC.presence_of_element_located((By.CLASS_NAME,grid_classname)),
            message=f"Grid element with classname '{grid_classname}' not found in time."
        )
        grid_elements = grid.find_elements(By.CLASS_NAME, "c-kOgFh")
        return grid_elements
    
    def find_all_elements_ref(self,classname:str)->list[WebElement]:
        elements = WebDriverWait(self.driver, Timeouts.waitForAResourceToAppear).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, classname)),
            message=f"Elements with classname '{classname}' not found in time."
        )
        return elements
    
    def find_element_ref(self,classname:str)->WebElement:
        element = WebDriverWait(self.driver, Timeouts.waitForAResourceToAppear).until(
            EC.presence_of_element_located((By.CLASS_NAME, classname)),
            message=f"Element with classname '{classname}' not found in time."
        )
        return element

    def find_element_ref_by_id(self,element_id:str)->WebElement:
        element = WebDriverWait(self.driver, Timeouts.waitForAResourceToAppear).until(
            EC.presence_of_element_located((By.ID, element_id)),
            message=f"Element with ID '{element_id}' not found in time."
        )
        return element
    
    def find_all_elements_ref_by_id(self,element_id:str)->list[WebElement]:
        elements = WebDriverWait(self.driver, Timeouts.waitForAResourceToAppear).until(
            EC.presence_of_all_elements_located((By.ID, element_id)),
            message=f"Element with ID '{element_id}' not found in time."
        )
        return elements
    
    def find_all_elements_starts_with(self,div_statement:str)->list[WebElement]:
        elements = WebDriverWait(self.driver, Timeouts.waitForAResourceToAppear).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, div_statement)),
            message=f"Element with '{div_statement}' not found in time."
        )
        return elements


    def click_grid_element(self, grid_elements_ref:list[WebElement], index):
        self.driver.execute_script("arguments[0].click();", grid_elements_ref[index])

    def wait_until_page_loaded(self, timeout=15):
        start_time = time.time()
        while True:
            try:
                state = self.driver.execute_script("return document.readyState")
                print(f"📄 Estado actual: {state}")  # Agregado para debug

                if state == "complete":
                    return True

            except Exception as e:
                print(f"⚠️ Error ejecutando JS: {e}")
                break

            if time.time() - start_time > timeout:
                print("⏰ Timeout esperando que se cargue la página.")
                break

            time.sleep(0.5)
        return False

    def navigate_back(self):

        content_routes = self.find_all_elements_ref("c-kzvPMu")
        # Hacer clic en la ruta anterior
        self.driver.execute_script("arguments[0].click();", content_routes[-1])