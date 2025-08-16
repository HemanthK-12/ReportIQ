FROM mcr.microsoft.com/devcontainers/python:3.10

WORKDIR /app

COPY requirements.txt /app

RUN apt update -y 
RUN apt install python3 python3-pip -y
RUN pip install --upgrade pip
RUN apt install -y python3-dev build-essential libatlas-base-dev gfortran libffi-dev graphviz
RUN pip install -r /app/requirements.txt

EXPOSE 3008

COPY . /app


ENTRYPOINT ["streamlit", "run"]

CMD [ "./app.py","--server.port", "3008" ]
