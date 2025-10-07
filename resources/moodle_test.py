
import re
from db.mongodb import MongoDB
import undetected_chromedriver as uc
import logging

from resources.functions import Functions
from models.question import Question
from utils.timeouts import Timeouts
from utils.constants import Constants
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.common.by import By
import requests
import base64
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select

import time


class MoodleTest:
    def __init__(self, driver:uc.Chrome,db:MongoDB):
        self.db = db
        self.driver = driver
        self.functions = Functions(driver)

        self.logger = logging.getLogger(self.__class__.__name__)  # Logger propio por clase
        self.course_info = ""

    def run(self):
        pass

    def explore_moodle(self):
        while True:
            try:
                breadcrumb = self.functions.find_all_elements_ref("breadcrumb-item")
                self.course_info = breadcrumb[2].text.split(',')[0]
                print(f"Curso actual: {self.course_info}")

            except Exception as e:
                continue

            try:              
                self.find_questions()            
            
            except TimeoutException:
                continue
            except Exception as e:
                self.logger.error(f"Error inesperado: {e}")
                return

    def find_questions(self):
        questions = self.functions.find_all_elements_starts_with("div[id^='question-']")
        if len(questions) == 1:
            #Caso ideal, una sola pregunta en la página
            try:
                class_info = questions[0].get_attribute("class")
                if "multichoice" in class_info:
                    self.do_multichoice_question(questions[0])
                # elif "ddwtos" in class_info:
                #     self.logger.info("Pregunta de emparejamiento detectada, no implementada aún.")          
                #     self.do_ddwtos_question(questions[0])
                elif "match" in class_info:
                    self.do_match_question(questions[0])                    

            except Exception as e:
                self.logger.error(f"Error al procesar la pregunta:{e}")
        
        else:
            #Caso raro, varias preguntas en la página
            self.logger.info("Se encontró varias preguntas en la página.")
            try:
                list_questions_to_save = []
                info_box = self.functions.find_element_ref("rui-summary-table")
            except Exception as e:
            
                for question in questions:
                    list_questions_to_save:list[Question] = []
                    try:
                        class_info = question.get_attribute("class")
                        if "multichoice" in class_info:
                            self.do_multichoice_question2(question,list_questions_to_save)
                        elif "match" in class_info:
                            self.do_match_question2(question,list_questions_to_save)                    

                    except Exception as e:
                        self.logger.error(f"Error al procesar la pregunta:{e}")
                    time.sleep(2)

            try:
                table_responsive = self.functions.find_element_ref("table-responsive")
                if len(list_questions_to_save) > 0:
                        for q in list_questions_to_save:
                            print(q)
                            # self.db.insert_question(self.course_info,q.to_dict())
            except Exception as e:
                pass

            

    def do_ddwtos_question(self, web_element: WebElement):
        question = web_element.find_element(By.CLASS_NAME, "qtext")
        print(question.text)
        # img_element = web_element.find_element(By.CLASS_NAME, "img-fluid")
        # img_src = question.get_attribute("src")
        # print(f"Imagen encontrada en la pregunta: {img_src}")
        espacios = web_element.find_elements(By.CSS_SELECTOR, "span.drop")
        print(f"Se encontraron {len(espacios)} espacios")
        # Encontrar todas las opciones a arrastrar
        opciones = web_element.find_elements(By.CSS_SELECTOR, "span.draghome.unplaced")
        print(f"Se encontraron {len(opciones)} opciones")
        for i, opcion in enumerate(opciones, start=1):
            print(f"Opción {i}: '{opcion.text.strip()}'")

        actions = ActionChains(self.driver)
        actions.drag_and_drop(opciones[1], espacios[0]).perform()
        actions.drag_and_drop(opciones[3], espacios[1]).perform()
        actions.drag_and_drop(opciones[5], espacios[2]).perform()
        time.sleep(5)  # Pausa para inspeccionar

    def do_match_question(self, web_element: WebElement):
        question = Question()
        question.question = web_element.find_element(By.CLASS_NAME, "qtext").text
        question.type = "match"
        flag_answer_question = False

        # selects_elements = web_element.find_elements(By.CSS_SELECTOR, "td.control select")
        list_selects_select: list[Select] = []


        #     # select.select_by_index(1)  # Seleccionar la primera opción válida
        if question.question != "":
            db_question = self.db.get_question(self.course_info,re.escape(question.question))  # Verificar si la pregunta ya existe en la base de datos
            
            if db_question != None:
                flag_answer_question = True
                
            table_rows = web_element.find_elements(By.CSS_SELECTOR, "table.answer tr")
            
            for i, fila in enumerate(table_rows, start=1):
                texto_pregunta = fila.find_element(By.CSS_SELECTOR, "td.text").text.strip()
                question.answers_text.append(texto_pregunta)
                # print(f"Fila {i} - Pregunta: '{texto_pregunta}'")
                
                select_element = fila.find_element(By.CSS_SELECTOR, "td.control select")
                select = Select(select_element)
                list_selects_select.append(select)

                options = [opt.text.strip() for opt in select.options if opt.get_attribute("value") != "0"]
                question.options.append(options)
                # print(f"Fila {i} - Opciones: {options}")
                
                if flag_answer_question:
                    # select.select_by_value(db_question['answers'][i-1])
                    select.select_by_index(options.index(db_question['answers'][i-1])+1)  # +1 porque el índice 0 es "Eleg
                    
    
            while True:
                list_answer_text = []
                try:
                    for s in list_selects_select:
                        selected_option = s.first_selected_option.text.strip()
                        if "Elegir" in selected_option :
                            continue
                        list_answer_text.append(selected_option)
                    
                    if len(list_answer_text) == len(list_selects_select):
                        list_captured_answers = list_answer_text

                except Exception as e:
                    pass
                
                if self.is_new_question(question.question):                                 
                    break


            if len(list_captured_answers)>0:
                question.answers = list_captured_answers     
                print(question)   
                self.db.insert_question(self.course_info,question.to_dict())


        time.sleep(1)  # Pausa para inspeccionar

    def do_multichoice_question2(self, web_element: WebElement, list_questions_to_save: list[Question]):  
        question = Question()
        question.question = web_element.find_element(By.CLASS_NAME, "qtext").text
        question.type = "multichoice"
        flag_answer_question = False

        if question.question != "":               
            db_question = self.db.get_question(self.course_info,re.escape(question.question))  # Verificar si la pregunta ya existe en la base de datos
            
            if db_question != None:
                flag_answer_question = True      
            

            answer_block = web_element.find_element(By.CLASS_NAME, "answer")
            options = answer_block.find_elements(By.CSS_SELECTOR, "div[class^='r']")
            # print(f"Número de opciones encontradas: {len(options)}")
            
            for option in options:
                #input_element = option.find_element(By.CSS_SELECTOR, "input[type='radio']")
                # input_element.click() #Si vale para seleccionar la respuesta
                option_text = self.get_text_from_option_element(option, "input[type='radio']")
                question.options.append(option_text)
                if flag_answer_question:
                    if option_text == db_question['answers'][0]:
                        input_element = option.find_element(By.CSS_SELECTOR, "input[type='radio']")
                        input_element.click()
                        flag_answer_question = False 

            captured_answer = ""
            try:  
                answer_text = self.get_text_from_option_element(web_element, "input[type='radio']:checked")
                if answer_text:
                    captured_answer = answer_text 
            except Exception as e:
                pass
            
            if captured_answer != "":
                question.answers.append(captured_answer)        
                list_questions_to_save.append(question)
    
    def do_match_question2(self, web_element: WebElement,list_questions_to_save: list[Question]):
        question = Question()
        question.question = web_element.find_element(By.CLASS_NAME, "qtext").text
        question.type = "match"
        flag_answer_question = False

        # selects_elements = web_element.find_elements(By.CSS_SELECTOR, "td.control select")
        list_selects_select: list[Select] = []


        #     # select.select_by_index(1)  # Seleccionar la primera opción válida
        if question.question != "":
            db_question = self.db.get_question(self.course_info,re.escape(question.question))  # Verificar si la pregunta ya existe en la base de datos
            
            if db_question != None:
                flag_answer_question = True
                
            table_rows = web_element.find_elements(By.CSS_SELECTOR, "table.answer tr")
            
            for i, fila in enumerate(table_rows, start=1):
                texto_pregunta = fila.find_element(By.CSS_SELECTOR, "td.text").text.strip()
                question.answers_text.append(texto_pregunta)
                # print(f"Fila {i} - Pregunta: '{texto_pregunta}'")
                
                select_element = fila.find_element(By.CSS_SELECTOR, "td.control select")
                select = Select(select_element)
                list_selects_select.append(select)

                options = [opt.text.strip() for opt in select.options if opt.get_attribute("value") != "0"]
                question.options.append(options)
                # print(f"Fila {i} - Opciones: {options}")
                
                if flag_answer_question:
                    # select.select_by_value(db_question['answers'][i-1])
                    select.select_by_index(options.index(db_question['answers'][i-1])+1)  # +1 porque el índice 0 es "Eleg
            

            
            list_answer_text = []
            list_captured_answers = []
            try:
                for s in list_selects_select:
                    selected_option = s.first_selected_option.text.strip()
                    if "Elegir" in selected_option :
                        continue
                    list_answer_text.append(selected_option)
                
                if len(list_answer_text) == len(list_selects_select):
                    list_captured_answers = list_answer_text

            except Exception as e:
                pass
            


            if len(list_captured_answers)>0:
                question.answers = list_captured_answers     
                list_questions_to_save.append(question)
            
            
                

    def do_multichoice_question(self, web_element: WebElement):    

        question = Question()
        question.question = web_element.find_element(By.CLASS_NAME, "qtext").text
        question.type = "multichoice"
        flag_answer_question = False

        if question.question != "":               
            db_question = self.db.get_question(self.course_info,re.escape(question.question))  # Verificar si la pregunta ya existe en la base de datos
            
            if db_question != None:
                flag_answer_question = True      
            

            answer_block = web_element.find_element(By.CLASS_NAME, "answer")
            options = answer_block.find_elements(By.CSS_SELECTOR, "div[class^='r']")
            # print(f"Número de opciones encontradas: {len(options)}")
            
            for option in options:
                #input_element = option.find_element(By.CSS_SELECTOR, "input[type='radio']")
                # input_element.click() #Si vale para seleccionar la respuesta
                option_text = self.get_text_from_option_element(option, "input[type='radio']")
                question.options.append(option_text)
                if flag_answer_question:
                    if option_text == db_question['answers'][0]:
                        input_element = option.find_element(By.CSS_SELECTOR, "input[type='radio']")
                        input_element.click()
                        flag_answer_question = False 
            
            while True:  
                answer_text = self.get_text_from_option_element(web_element, "input[type='radio']:checked")
                if answer_text:
                    captured_answer = answer_text 
                
                if self.is_new_question(question.question):                    
                    break
            
            if captured_answer:
                question.answers.append(captured_answer)        
                print(question)
                self.db.insert_question(self.course_info,question.to_dict())

    def get_text_from_option_element(self, element_question: WebElement, css_statement:str) -> str:
        
        try:
            
            selected_input = element_question.find_element(By.CSS_SELECTOR, css_statement)
            
            try:
                label_id = selected_input.get_attribute("aria-labelledby")
                label_element = element_question.find_element(By.ID, label_id)
                # Texto visible de la respuesta
                option_info = label_element.text.strip()
                option_split = option_info.split("\n")
                if len(option_split) ==2:
                    variable, option_text = option_info.split("\n") #TODO igual ponerlo en un try catch porque no sabemos como estara redactada la opcion
                    # print(option_text)
                    return option_text
                elif len(option_split)>2:
                    option_text = "".join(option_split[1::])
                    # print(option_text)
                    return option_text
                else:
                    print("⚠️ La opción no tiene el formato esperado.")
                    print(option_info)
                    return ""
            
            except Exception as e:            
                # self.logger.error(f"Error al verificar opción seleccionada: {e}")
                # self.logger.error(f" O Error al consultar texto de la opción, hay imagenes??:")
                time.sleep(1)
                return ""
            
        except Exception as e:
            self.logger.error(f"Error al obtener opción: {e}")
            time.sleep(1)
            return ""

    def get_question(self) -> str:
        try:
            question_element = self.functions.find_all_elements_starts_with("div[id^='question-'] .qtext")
            return question_element[0].text if question_element else ""
        except Exception as e:
            print(e)
            return ""
        

    def is_new_question(self, question: str) -> bool:
        if self.get_question() != question:
            return True
        
    
    def download_image(self, url: str):
        pass


    # print(f"Pregunta: {question.question}")

# try:
#     img_element = web_element.find_element(By.CLASS_NAME, "img-fluid")
#     img_src = img_element.get_attribute("src")
#     question.img_source_question.append(img_src)
#     print(f"Imagen encontrada en la pregunta: {img_src}")
#     # Extraer cookies de la sesión Selenium
#     cookies = self.driver.get_cookies()
#     s = requests.Session()
#     for cookie in cookies:
#         s.cookies.set(cookie['name'], cookie['value'])

#     # Descargar la imagen usando la sesión autenticada
#     url = "https://aulanivelacion.unemi.edu.ec/pluginfile.php/227151/question/questiontext/510815/3/733925/Captura%20de%20pantalla%202024-04-16%20a%20la%28s%29%204.59.28%E2%80%AFp.%C2%A0m..png"
#     resp = s.get(url)

#     if resp.status_code == 200:
#         img_bytes = resp.content
#         img_b64 = base64.b64encode(img_bytes).decode("utf-8")
#         print("✅ Imagen en Base64 lista:")
#         print(img_b64[:200], "...")  # solo mostramos un pedazo
#     else:
#         print("⚠️ Error al obtener la imagen:", resp.status_code)
# except Exception as e:
#     self.logger.info("No se encontró imagen en la pregunta.")
    