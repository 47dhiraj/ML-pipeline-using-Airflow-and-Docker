from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator



# creates a default_args for DAG object
default_args = {
    'owner': 'dhiraj47',
    'depends_on_past': False,               
    'email_on_failure': False,
    'email_on_retry': False,
    # 'retries': 1,                            
    # 'retry_delay': timedelta(minutes=3),               
}


# Creating/Declaring a DAG Object
dag = DAG(
    dag_id='my_testing_dag',
    default_args=default_args,
    description='Just for Testing Purpose',
    start_date=datetime(2024, 2, 23),
    schedule_interval=None,                   
    catchup=False,
)


# First Task: To execute bash Command
bash_task_test = BashOperator(
    task_id="bash_task_test",
    bash_command='echo "Testing bash script executed successfully !!" ',
    dag=dag
)


# Since, only one task, so, no required of task dependency execution order
