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



# train_and_test_recommendation_model() is custom function/method
def train_and_test_recommendation_model():
    
    # Loading .csv datasets
    movies = pd.read_csv('https://raw.githubusercontent.com/47dhiraj/Movie-Recommendation-System-Django-and-ML/main/dataset/movies.csv')
    ratings = pd.read_csv('https://raw.githubusercontent.com/47dhiraj/Movie-Recommendation-System-Django-and-ML/main/dataset/ratings.csv')


    # Data cleaning and manipulation
    ratings = pd.merge(movies, ratings).drop(['genres','timestamp'], axis=1) 
    user_ratings = ratings.pivot_table(index=['userId'], columns=['title'], values='rating')
    user_ratings = user_ratings.dropna(thresh=10, axis=1).fillna(0)


    # using pearson coorelation algorithm
    item_similarity_df = user_ratings.corr(method='pearson')


    # Saving the trained model in .pkl file format
    item_similarity_df.to_pickle('item_similarity_df.pkl')

    # Loading the saved .pkl model
    item_similarity_df = pd.read_pickle('item_similarity_df.pkl')


    # Core function to get similar movies
    def get_similar_movies(movie_name,user_rating):
        similar_score = item_similarity_df[movie_name]*(user_rating-2.5)
        similar_score = similar_score.sort_values(ascending=False)
        return similar_score
    

    scifi_lover = [("The Martian", 5)]

    similar_movies = pd.DataFrame()

    for movie,rating in scifi_lover:
        similar_movies = similar_movies._append(get_similar_movies(movie,rating), ignore_index=True)
    

    all_recommend = similar_movies.sum().sort_values(ascending=False)

    print(all_recommend)
    print('Recommendation model trained & tested successfully !!')



# Declaring a DAG object
ml_dag = DAG(
    dag_id='ml_pipeline_dag',                         
    default_args=default_args,        
    description='ML pipeline for Recommendation System',
    start_date=datetime(2024, 2, 25),
    catchup=False,
)



# Setting our first task (i.e to train the recommendation model)
task1 = PythonOperator(
    task_id='recommendation_model_training_and_testing',     
    python_callable=train_and_test_recommendation_model,         
    dag=ml_dag,
)

