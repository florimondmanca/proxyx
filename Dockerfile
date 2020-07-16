FROM python:3.7

WORKDIR /usr/app
ADD ./requirements.txt /usr/app
RUN pip install -r requirements.txt

ADD ./proxycore.py /usr/app

ARG PROXYCORE_HOSTNAME
ENV PROXYCORE_ROOT_PATH=""

CMD python -m uvicorn --host 0.0.0.0 --port 8000 proxycore:app
