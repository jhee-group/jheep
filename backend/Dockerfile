# pull official base image
FROM python:3.10-slim

ARG JHEE_CNS_VERSION

# set environment variables
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
 && apt-get -y install netcat gcc postgresql-common supervisor \
 && apt-get -y autoclean \
 && apt-get -y autoremove --purge \
 && rm -rf /var/lib/apt/lists/*
 
# set working directory
ENV CNS_APP_DIR /backend
WORKDIR ${CNS_APP_DIR}

# install cns
RUN pip install --upgrade pip
#COPY ./requirements.txt ${APP_DIR}
#RUN pip install -U -r ${APP_DIR}/requirements.txt
COPY . ${CNS_APP_DIR}
RUN pip install -U -e .

# entrypoint
#ENTRYPOINT jhee run
COPY ./supervisord.conf /etc/supervisord.conf
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
