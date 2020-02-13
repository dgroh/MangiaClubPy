FROM python:3

MAINTAINER Daniel Groh

COPY app /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]