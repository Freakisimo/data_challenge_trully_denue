from bs4 import BeautifulSoup
from urllib.parse import urlparse

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
    base_path: str, 
    hrefText: str=None
) -> list:

    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    try:
        driver.implicitly_wait(30)
        driver.get(url)
        time.sleep(10)
        innerHTML = driver.execute_script("return document.body.innerHTML")
        driver.quit()
    except Exception as e:
        logging.error(e)
        driver.quit()

    soup = BeautifulSoup(innerHTML, 'html.parser')
    rows = soup.findAll("tr")

    links = {}
    for r in rows:
        if r.get('data-agrupacion') == 'denue' and r.get('data-nivel') == '3' and \
            'COVID-19' not in r.get('data-titulo') and '2015' not in r.get('data-titulo'):
            safe_key = safe_path(r.get('data-titulo', ''))
            key = safe_key.replace('|', '/').replace('otros/denue/','')
            start, end = key.find('(')-1, key.find(')')+1
            if start and end:            
                key = key.replace(key[start:end], '')
            hrefs = [l.get('href') for l in r.findAll('a') if hrefText in l.get('href', '')]
            if hrefs:
                links.setdefault(key, []).append(hrefs[0])
    
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    files = []
    for path, links in links.items():
        base = urlparse(url).netloc
        for link in links:
            file_url = f'http://{base}{link}'
            file = requests.get(file_url, stream=True)
            fnam = link.rsplit('/', 1)[-1]
            start, end = fnam.find('('), fnam.find(')')+1
            if start and end:            
                file_name = fnam.replace(fnam[start:end], '').replace('_denue_', '/')
            else:
                file_name = fnam.replace('denue_', '/')
            file_path = safe_path(f"{base_path}{path}{file_name}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path,"wb") as f:
                for chunk in file.iter_content(chunk_size=16384):  
                    if chunk:
                        f.write(chunk)
            files.append(file_path)
            time.sleep(1)
            break

    return files