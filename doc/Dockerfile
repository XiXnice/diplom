FROM python:3.10

WORKDIR /usr/src/mycite

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .