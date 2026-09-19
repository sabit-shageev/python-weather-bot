FROM python:3.11.15-slim

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/app/src

RUN apt update 

COPY ./requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY src/ ./src/


# Запускаем бота
CMD ["python", "-m", "src.main"]

