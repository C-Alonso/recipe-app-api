FROM python:3.7-alpine
MAINTAINER Carlos Alonso

# So the outputs are printed directly (insted of being buffered)
ENV PYTHONUNBUFFERED 1

# Copy and install the requirements
COPY ./requirements.txt /requirements.txt
# It uses the package manager (apk) that comes with alpine
# and adds an update, telling not to store the registry index
# on our Docker file. We keep the footprint at minimum.
RUN apk add --update --no-cache postgresql-client jpeg-dev
# The following are necessary packages install the requirements
# correctly. They will be disposed after the installation.
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
# Delete temporary dependencies.
RUN apk del .tmp-build-deps

# Create empty folder
RUN mkdir /app
# And declare it as default folder
WORKDIR /app
COPY ./app /app

# Create a directory that will contain resources that may have to be shared
# with other containers (f.e.: Web-server serving images).
# The following 2 folders are used as standard in django.
# (-p: create if doesn't exist).
RUN mkdir -p /vol/web/media
# Create a directory for static files (JS, CSS)
RUN mkdir -p /vol/web/static

# Create a (Linux) user that will be used to run the processes from the project.
# This way, the root user will not be the one running the processes,
# and the vulnerability gaps are shortened.
RUN adduser -D user
# Sets the ownership of /vol (and everything in it [R -> Recursive]) to user.
RUN chown -R user:user /vol
# The user has all permissions, the rest, can only read and write.
RUN chmod -R 755 /vol/web
USER user