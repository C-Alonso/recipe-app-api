FROM python:3.7-alpine
MAINTAINER Carlos Alonso

# So the outputs are printed directly (insted of being buffered)
ENV PYTHONUNBUFFERED 1

# Copy and install the requirements
COPY ./requirements.txt /requirements.txt
# It uses the packaga manager (apk) that comes with alpine
# and adds an update, telling not to store the registry index
# on our Docker file. We keep the footprint at minimum.
RUN apk add --update --no-cache postgresql-client
# The following are necessary packages install the requirements
# correctly. They will be disposed after the installation.
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
# Delete temporary dependencies.
RUN apk del .tmp-build-deps

# Create empty folder
RUN mkdir /app
# And declare it as default folder
WORKDIR /app
COPY ./app /app

# Create a (Linux) user that will be used to run the processes from the project.
# This way, the root user will not be the one running the processes,
# and the vulnerability gaps are shortened.
RUN adduser -D user
USER user