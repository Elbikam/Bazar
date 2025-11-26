
from selenium import webdriver
from selenium.webdriver.common.by import By
import time 

class ComponentDriver(webdriver.Chrome):
    """page """


    def login(self,live_server_url):
        self.get(f"{live_server_url}/dashboard/login/")
        time.sleep(4)
        username_input = self.find_element(By.NAME, "username")
        username_input.send_keys("b-elbikam")
        password_input = self.find_element(By.NAME, "password")
        password_input.send_keys("Admin1234")
        self.find_element(By.NAME,"Login").click()

    def get_report_detail(self,live_server_url):
        self.get(f"{live_server_url}/dashboard/ai_report")
        time.sleep(4)