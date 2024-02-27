FROM apache/airflow:2.5.1

USER supersetuser

RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y default-libmysqlclient-dev


CMD ["superset", "run", "-p", "8088", "-h", "0.0.0.0"]
