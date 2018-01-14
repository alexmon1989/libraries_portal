FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get -y install xvfb libfontconfig wkhtmltopdf

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/