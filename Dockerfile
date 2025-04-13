FROM apache/airflow:2.8.1-python3.8

USER root
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install dependencies 
RUN pip install PyGithub tqdm curtsies google-cloud-storage

# Copy your dags, plugins, and scripts
COPY dags /opt/airflow/dags
COPY plugins /opt/airflow/plugins
COPY scripts /app/scripts
COPY dags/application_default_credentials.json /app/application_default_credentials.json
COPY dags/token.txt /app/token.txt

# Set PYTHONPATH to include the /app directory
ENV PYTHONPATH="/app"
