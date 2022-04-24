FROM python:3.10-slim

WORKDIR /flaskProject
ADD . /flaskProject

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
ENV FLASK_APP=app.py

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]

