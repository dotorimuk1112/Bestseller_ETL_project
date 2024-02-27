# [출처] [Airflow] Yes24 Best 200 책 정보 수집 & Superset으로 일별 모니터링 대시보드 구축|작성자 요다
from datetime import datetime
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from craw_books import get_books
from to_postgres import save_to_postgres
# from custom_xcom import CustomXCom

def complete():
    print("yes24_top_200_수집 완료")

default_args = {
   "start_date" : datetime(2023, 1, 1),
    "retry" : 3
}

# DAG 정의
with DAG(
    dag_id="yes24_book_pipeline",
    schedule_interval="@daily",
    default_args=default_args,
    tags=['book', 'yes24', 'api'],
    catchup=False,
) as dag:
    creating_table = PostgresOperator(
    task_id="creating_table",
    postgres_conn_id="airflow-superset",
    sql='''
    CREATE TABLE IF NOT EXISTS yes_book(
    rank integer,
    title TEXT,
    author text,
    price integer,
    publishing_house text,
    publication_date text,
    review_count integer,
    link text
    )
    '''
    )

    get_data_result = PythonOperator(
    task_id="get_books",
    python_callable=get_books,
    provide_context=True,  # 이 값을 True로 설정하여 컨텍스트(포함하여 XCom)를 함수로 전달합니다
    dag=dag  # DAG를 작업에 전달합니다
    )

    save_postgres = PythonOperator(
    task_id="save_postgres",
    python_callable=save_to_postgres,
    dag=dag
    )
    
    # 대그 완료 출력
    print_complete = PythonOperator(
            task_id="print_complete",
            python_callable=complete # 실행할 파이썬 함수
    )

    creating_table >> get_data_result >> save_postgres >> print_complete