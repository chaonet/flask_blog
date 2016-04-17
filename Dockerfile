FROM python:2.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD gunicorn run:app -b 0.0.0.0:8000