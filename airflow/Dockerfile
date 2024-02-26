# Use the official Airflow base image, release version 2.8.1
FROM apache/airflow:2.8.1

RUN pip install apache-airflow-providers-docker

COPY requirements.txt .

RUN pip install -r requirements.txt