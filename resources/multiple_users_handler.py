import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from resources.altissia_webdriver import AltissiaWebDriver
from models.user_credentials import User
from db.mongodb import MongoDB
from resources.logger import LoggerConfigurator
from utils.constants import Constants

class MultipleUsersHandler:
    def __init__(self,max_chrome_sessions,log_file_name="errores.log"):
        
        self.max_chrome_sessions = max_chrome_sessions
        self.results = []

        #configurar logging
        LoggerConfigurator.configure(log_file_name)
        self.logger = logging.getLogger(self.__class__.__name__)  # Logger propio por clase

        # Inicializar MongoDB
        self.mongoDB = MongoDB()
        # self.mongoDB.generate_pdf()

    def print_report(self):
        pass

    def webscrap(self, index: int):
        start = time.time()
        try:
            altissiaWebScrapping = AltissiaWebDriver(Constants.urlToScrap,self.mongoDB,index)
            altissiaWebScrapping.run()
            return (index, round(time.time() - start, 2), None)

        except Exception as e:
            self.logger.error(f"Error en sesión {index}: {e}")
            time.sleep(8)  # Esperar antes de reintentar
            return (index, round(time.time() - start, 2), str(e))
        
        finally:            
            if altissiaWebScrapping:
                altissiaWebScrapping.cleanup()

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_chrome_sessions) as executor:
            futures = {executor.submit(self.webscrap,index): index for index in range(self.max_chrome_sessions)}
            for f in tqdm(as_completed(futures), total=self.max_chrome_sessions, desc="Resolviendo modulos de ingles"):
                self.results.append(f.result())

        self.print_report() 