from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator



# default_args for DAG
default_args = {
    'owner': 'dhiraj47',
    'depends_on_past': False,                
    'email_on_failure': False,
    'email_on_retry': False,
}


# Creating/Declaring a DAG Object
bash_dag = DAG(
    dag_id='my_testing_dag',
    default_args=default_args,
    description='Just for Testing Purpose',
    start_date=datetime(2024, 2, 24),
    schedule_interval=None,                   
    catchup=False,
)


# First task
bash_task_test = BashOperator(
    task_id="bash_task_test",
    bash_command='echo "Testing bash script executed successfully !!" ',
    dag=bash_dag
)

