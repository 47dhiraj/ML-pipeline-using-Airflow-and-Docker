# Use the official Airflow base image
FROM apache/airflow:2.8.1

# Install the apache airflow providers
RUN pip install apache-airflow-providers-docker


COPY requirements.txt .

RUN pip install -r requirements.txt