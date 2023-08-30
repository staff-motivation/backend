FROM python:3.9-slim

RUN mkdir /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY backend/ /app

WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]