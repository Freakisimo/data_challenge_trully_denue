from unicodedata import normalize

import os
import zipfile
import boto3
import pandas as pd
import time


def get_files(root: str) -> list:
    return [os.path.join(path, name) 
            for path, subdirs, files in os.walk(root)
            for name in files]

def safe_path(path: str) -> str:
    trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
    to_lower = path.lower()
    comma = to_lower.replace(" ", "_")
    spaces = comma.replace(",", "")
    normalized = normalize('NFKC', normalize('NFKD', spaces).translate(trans_tab))
    return normalized


def unzip_files(root: str) -> None:
    files = get_files(root)

    local_files = []
    for f in files:
        if f.endswith('.zip'):
            f_path = os.path.dirname(f)
            target_path = f"{f_path}/"
            with zipfile.ZipFile(f,"r") as zip_ref:
                zip_files = [f"{target_path}{zf}" for zf in zip_ref.namelist()]
                time.sleep(1)
                zip_ref.extractall(target_path)

            files.remove(f)

            if os.path.exists(f):
                os.remove(f)
            
            local_files += zip_files
        
    local_files += files

    local_files = [lf for lf in local_files if os.path.isfile(lf)]
    local_files = [lf for lf in local_files if '__MACOSX' not in lf]

    for idx,lf in enumerate(local_files, start=0):
        lf_safe = safe_path(lf)
        dir_path = os.path.dirname(lf_safe)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        os.rename(lf, lf_safe)
        local_files[idx] = lf_safe



def xlsx_to_csv(files: list) -> list:
    local_files = []
    for f in files:
        if f.endswith('.xlsx') or f.endswith('.xls'):
            path = os.path.splitext(f)[0]
            read_file = pd.read_excel(f)
            read_file.to_csv (f'{path}.csv', index=None, header=True)

            files.remove(f)

            if os.path.exists(f):
                os.remove(f)

            local_files.append(f'{path}.csv')

    local_files += files

    return local_files 
    

def upload_s3_files(
    root: str, 
    start_path: str, 
    bucket: str, 
    fiter_path: str='',
    prefix: str=''
) -> None:
    files = get_files(root)

    print(files)

    return

    s3_client = boto3.client('s3')
    for f in files:
        r_path = os.path.relpath(f, start_path)
        object_name = f"{prefix}{r_path}"
        try:
            s3_client.upload_file(f, bucket, object_name)
        except Exception as e:
            print(e)

