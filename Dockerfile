FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml pdm.lock /app/
RUN apt-get update -y
RUN apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential
RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false

COPY ./src/ /app/

RUN pdm install -p /app -g

CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
