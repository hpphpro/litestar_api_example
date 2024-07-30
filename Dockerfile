FROM python:3.12.4

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY . .

COPY wait.sh /wait.sh

RUN chmod +x /wait.sh

RUN pip install --upgrade pip && \ 
    pip install --no-cache-dir -r requirements.txt
