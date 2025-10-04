import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from models.user_credentials import User
from utils.timeouts import Timeouts
from db.mongodb import MongoDB
import logging
from resources.functions import Functions
from utils.constants import Constants

class Authenticator:
    def __init__(self, driver:uc.Chrome, user:User,db:MongoDB):
        self.logger = logging.getLogger(self.__class__.__name__)  # Logger propio 

        self.user = user
        self.functions = Functions(driver)

    def login(self) -> bool:
        try:
            self.functions.wait_until_page_loaded()

            username_input = self.functions.find_element_ref_by_id(Constants.emailInputId)      
            username_input.send_keys(self.user.username)

            # password_input = self.functions.find_element_ref(Constants.passwordInputClass)   #NOTE: Uncomment this for real test login
            password_input = self.functions.find_element_ref_by_id(Constants.passwordInputId)
            password_input.send_keys(self.user.password)

            login_button = self.functions.find_element_ref(Constants.loginButtonClass)
            login_button.click()

            #TODO Add code to verify login session 
            return True

        except Exception as e:
            messages = str(e).split("\n")    
            self.logger.error(f"Authentication failed " + messages[0], extra={'user': self.user.username})        
            raise Exception(f"English Test Failed")
            # raise Exception(f"Authentication failed for user {self.user.username}, " + messages[0]) 
            
            


        

        




        
