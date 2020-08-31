FROM python:3.8-alpine

WORKDIR /opt/eda

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-m", "eda.cli"]
