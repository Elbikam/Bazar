
from .component_driver import ComponentDriver
import time 
class ApplicationRunner():
    """User joureny"""
    def __init__(self,driver:ComponentDriver,url):
        self.driver = driver
        self.url = url
        
        

    def run(self):
        self.driver.login(self.url)

    def get_report(self):
        self.driver.get_report_detail(self.url)