# Тестовый ("Hello world") пайплайн для Apache Airflow.
# После сохранения DAG появится в веб-интерфейсе (http://localhost:8080)

from datetime import datetime
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="hello_world",
    description="Тестовый пайплайн",
    start_date=datetime(2026, 6, 8),
    schedule=None,
    catchup=False,
    tags=["test"],
) as dag:
    say_hello = BashOperator(
        task_id="say_hello",
        bash_command='echo "Hello world"',
    )

    say_bye = BashOperator(
        task_id="say_bye",
        bash_command='echo "Pipeline finished"',
    )

    say_hello >> say_bye
