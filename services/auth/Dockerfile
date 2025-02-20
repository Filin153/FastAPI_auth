FROM python:3.10

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:1111