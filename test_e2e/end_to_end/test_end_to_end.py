from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .app_runner import ApplicationRunner
from .component_driver import ComponentDriver



class TestEndToEnd(StaticLiveServerTestCase):
    """Test each feature End_to_End """
    
   

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = ComponentDriver()
        cls.selenium.implicitly_wait(15)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_feature_user_login(self):
        app = ApplicationRunner(self.selenium,self.live_server_url)
        app.run()



    def test_generate_report_end_to_end(self):
        app = ApplicationRunner(self.selenium,self.live_server_url)
        app.get_report()