from airflow.hooks.base_hook import BaseHook
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.command import Command
import logging
import time


class SeleniumHook(BaseHook):
    
    def __init__(self):
        self.ip_add = None
        self.driver = None
        logging.info('initialised hook')


    def get_ip_add(self):
        logging.info('getting ip')
        # client = docker.DockerClient()
        # containers = client.containers.list()
        # wd = 'chrome_1'
        # chrome = [x for x in containers if wd in  x.name]
        # if chrome:
        #     container = chrome[0]
        #     network = container.name.replace(wd,'default')
        #     self.ip_add = container.attrs["NetworkSettings"]["Networks"][network]["IPAddress"]
        self.ip_add = '10.5.0.5'


    def create_driver(self):
        logging.info('creating driver')
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--disable-gpu")
        capabilities = DesiredCapabilities.CHROME.copy()
        chrome_driver = '{}:4444/wd/hub'.format(self.ip_add)
        while True:
            try:
                driver = webdriver.Remote(
                    command_executor=chrome_driver,
                    desired_capabilities=capabilities,
                    options=options
                )
                logging.info('remote ready')
                break
            except Exception as e:
                logging.error(e)
                logging.info('remote not ready, sleeping for ten seconds')
                time.sleep(10)
        self.driver = driver


    def run_script(self, script, args):
        script(self.driver, *args)

    
    def quit_driver(self):
        try:
            self.driver.execute(Command.STATUS)
            self.driver.quit()
            logging.info('Driver quit correctly')
        except:
            self.driver = None
            logging.error('Driver is dead')