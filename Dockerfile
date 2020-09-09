FROM python:3.7-alpine
MAINTAINER Carlos Alonso

#So the outputs are printed directly (insted of being buffered)
ENV PYTHONUNBUFFERED 1

#Copy and install the requirements
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#Create empty folder
RUN mkdir /app
#And declare it as default folder
WORKDIR /app
COPY ./app /app

#Create a user that will be used to run the processes from the project.
#This way, the root user will not be the one running the processes, and the vulnerability gaps are shortened.
RUN adduser -D user
USER user