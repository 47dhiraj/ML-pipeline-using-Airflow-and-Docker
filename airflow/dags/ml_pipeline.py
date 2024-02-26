from datetime import datetime, timedelta
from airflow import DAG

from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator

import pandas as pd

import pickle




# default_args for DAG
default_args = {
    'owner': 'dhiraj47',
    'depends_on_past': False,                  
    'email_on_failure': False,
    'email_on_retry': False,
    # 'retries': 1,                            
    # 'retry_delay': timedelta(minutes=1),              
}



# function to train model
def train_recommendation_model(**kwargs):
    
    # Loading .csv datasets
    movies = pd.read_csv('https://raw.githubusercontent.com/47dhiraj/Movie-Recommendation-System-Django-and-ML/main/dataset/movies.csv')
    ratings = pd.read_csv('https://raw.githubusercontent.com/47dhiraj/Movie-Recommendation-System-Django-and-ML/main/dataset/ratings.csv')

    # Data cleaning and manipulation
    ratings = pd.merge(movies, ratings).drop(['genres','timestamp'], axis=1) 
    user_ratings = ratings.pivot_table(index=['userId'], columns=['title'], values='rating')
    user_ratings = user_ratings.dropna(thresh=10, axis=1).fillna(0)


    # using pearson coorelation algorithm
    item_similarity_df = user_ratings.corr(method='pearson')

    print('Recommendation model trained successfully !!')

    ## Pushing data between task
    item_similarity_df_pkl_file = '/tmp/item_similarity_df.pkl'
    item_similarity_df.to_pickle(item_similarity_df_pkl_file)
    kwargs['task_instance'].xcom_push(key='item_similarity_df_pkl_file', value=item_similarity_df_pkl_file)




def test_recommendation_model(**kwargs):

    item_similarity_df_pkl_file = kwargs['task_instance'].xcom_pull(task_ids='recommendation_model_training', key='item_similarity_df_pkl_file')

    if item_similarity_df_pkl_file is None:
        print("Error: item_similarity_df_pkl_file is None")
        return
    else:
        print("Received item_similarity_df_pkl_file:", item_similarity_df_pkl_file)

        ## Loading the DataFrame 
        try:
            item_similarity_df = pd.read_pickle(item_similarity_df_pkl_file)
        except Exception as e:
            print("Error loading DataFrame from .pkl file:", str(e))
            return
        

        def get_similar_movies(movie_name,user_rating):
            similar_score = item_similarity_df[movie_name]*(user_rating-2.5)
            similar_score = similar_score.sort_values(ascending=False)
            return similar_score


        scifi_lover = [("The Martian", 5)]

        similar_movies = pd.DataFrame()

        for movie,rating in scifi_lover:
            similar_movies = similar_movies._append(get_similar_movies(movie,rating), ignore_index=True)

        all_recommend = similar_movies.sum().sort_values(ascending=False)

        print('Recommendation model tested successfully !!')

        ## Pushing data between task
        all_recommend_dict = all_recommend.to_dict()
        kwargs['task_instance'].xcom_push(key='all_recommend', value=all_recommend_dict)




def tune_recommendation_model(**kwargs):

    all_recommend_dict = kwargs['task_instance'].xcom_pull(task_ids='recommendation_model_testing', key='all_recommend')

    if all_recommend_dict is None:
        print("Error: all_recommend_dict is None")
        return
    else:
        print("Received all_recommend_dict:", all_recommend_dict)

        all_recommend = pd.Series(all_recommend_dict)

        check_name = ['The Martian']

        # Checking & eliminating, if the recommended movies is already seen ??
        def check_seen(movie, seen_movies):
            for item in seen_movies:
                if item == movie:
                    return True
            return False
        

        print('\nList of similar movies like',check_name, '\n')

        i = 0
        for movie, score in all_recommend.items():
            if not check_seen(movie, check_name):
                print(movie,'\t\t\t\t\t',  score)
                # print(movie)

            i = i + 1
            if i >= 36 + len(check_name):
                break





# Creating/Declaring a DAG object
ml_dag = DAG(
    dag_id='ml_pipeline_dag',                         
    default_args=default_args,        
    description='ML pipeline for Recommendation System',
    start_date=datetime(2024, 2, 26),
    catchup=False,
)


# Task to train the recommendation model)
model_train_task = PythonOperator(
    task_id='recommendation_model_training',     
    python_callable=train_recommendation_model,         
    dag=ml_dag,
)


# Task to test the recommendation model)
model_test_task = PythonOperator(
    task_id='recommendation_model_testing',     
    python_callable=test_recommendation_model,
    provide_context=True,     
    dag=ml_dag,
)


# Task too tune the recommendation model for better performance
model_tune_task = PythonOperator(
    task_id='recommendation_model_tuning',     
    python_callable=tune_recommendation_model,
    provide_context=True,     
    dag=ml_dag,
)


# Setting Task execution order
model_train_task >> model_test_task >> model_tune_task
