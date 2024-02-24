from datetime import datetime, timedelta
from airflow import DAG

from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator

import pandas as pd



# default_args for DAG
default_args = {
    'owner': 'dhiraj47',
    'depends_on_past': False,              
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,                             
    'retry_delay': timedelta(minutes=2),              
}




# train_recommendation_model() is custom function to train recommendation model
def train_recommendation_model():
    
    # Loading .csv datasets
    movies = pd.read_csv('https://raw.githubusercontent.com/47dhiraj/Movie-Recommendation-System-Django-and-ML/main/dataset/movies.csv')
    ratings = pd.read_csv('https://raw.githubusercontent.com/47dhiraj/Movie-Recommendation-System-Django-and-ML/main/dataset/ratings.csv')

    # Data cleaning and manipulation
    ratings = pd.merge(movies,ratings).drop(['genres','timestamp'],axis=1) 
    user_ratings = ratings.pivot_table(index=['userId'],columns=['title'],values='rating')
    user_ratings = user_ratings.dropna(thresh=10,axis=1).fillna(0)

    # using pearson coorelation algorithm
    item_similarity_df = user_ratings.corr(method='pearson') 

    print('Recommendation model trained successfully !!')



# Creating/Declaring a DAG object
ml_dag = DAG(
    dag_id='ml_pipeline_dag',                         
    default_args=default_args,        
    description='ML pipeline for Recommendation System',
    start_date=datetime(2024, 2, 24),
    catchup=False,
)



# Setting our first task (i.e to train the recommendation model)
task1 = PythonOperator(
    task_id='train_the_model',     
    python_callable=train_recommendation_model,         
    dag=ml_dag,
)

