from datetime import datetime, timedelta

from bs4 import Script
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from operators.selenium_operator import SeleniumOperator

from utils.get_files import selenium_scrapper 

default_args = {
    'owner': 'Freakisimo',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    default_args=default_args,
    dag_id='etl_denue',
    description='Download data from DENUE',
    start_date=datetime(2022, 9, 1),
    schedule_interval='@monthly'
) as dag:

    start = DummyOperator(
        task_id='start')
    
    get_data = SeleniumOperator(
        script=selenium_scrapper,
        script_args=['https://www.inegi.org.mx/app/descarga/',
                 '/tmp/denue/',
                 'a',
                 'csv.zip'],
    task_id='get_files')


    end = DummyOperator(
        task_id='end')

    start >> get_data >> end
