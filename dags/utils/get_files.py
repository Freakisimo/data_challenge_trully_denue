from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import os
import shutil
import re
import requests
import time
import logging

from utils.python_tools import safe_path

def selenium_scrapper(
    driver,
    url: str, 
    path: str, 
    label: str,
    hrefText: str=None
) -> list:


    if os.path.exists(path):
        shutil.rmtree(path)

    try:
        driver.implicitly_wait(30)
        driver.get(url)
        time.sleep(10)
        innerHTML = driver.execute_script("return document.body.innerHTML")
    except Exception as e:
        logging.error(e)
        driver.quit()

    soup = BeautifulSoup(innerHTML, 'html.parser')
    tables = soup.findAll("table")
    links = [a.get('href', '') for t in tables for a in t.findAll(label) if hrefText in a.get('href', '')]
    print(links)

    if not os.path.exists(path):
        os.mkdir(path)

    files = []
    for link in links:
        base = urlparse(url).netloc
        file_url = f'http://{base}{link}'
        file = requests.get(file_url, stream = True)
        file_name = link.rsplit('/', 1)[-1]
        file_path = safe_path(f"{path}{file_name}")
        with open(file_path,"wb") as shp:
            for chunk in file.iter_content(chunk_size=1024):  
                if chunk:
                    shp.write(chunk)
        
        files.append(file_path)
        break

    return files