import pandas as pd
from sqlalchemy import create_engine
from airflow.models import XCom
from io import StringIO  # 필요한 StringIO 추가

__all__ = ['save_to_postgres']

def save_to_postgres(**kwargs):
    ti = kwargs['ti']
    
    # XCom에서 CSV 문자열을 가져와 데이터프레임으로 변환
    csv_data = ti.xcom_pull(task_ids='get_books', key='data')
    df = pd.read_csv(StringIO(csv_data))
    print(df)
    
    # PostgreSQL 연결 정보 설정
    db_username = 'airflow'
    db_password = 'airflow'
    db_host = 'postgres'
    db_port = '5432'
    db_name = 'airflow'

    # SQLAlchemy 엔진 생성
    db_url = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(db_url)

    # DataFrame을 PostgreSQL 테이블로 적재
    table_name = 'yes_book'
    if csv_data:
        df.to_sql(table_name, engine, index=False, if_exists='replace')
        print(f"PostgreSQL 테이블 '{table_name}'에 성공적으로 적재되었습니다.")
    else:
        print(f"적재 중 오류 발생: {e}")