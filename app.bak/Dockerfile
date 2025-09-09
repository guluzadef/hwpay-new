FROM python:3.12-bullseye
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install django django-cors-headers

COPY . .

RUN pip install --upgrade pip setuptools
RUN pip install --default 1000 -r requirements.txt

EXPOSE 8000
