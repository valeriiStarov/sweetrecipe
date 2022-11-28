FROM python:3.9

WORKDIR /sweetrecipe

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# RUN apk update \
#      && apk add zlib-dev jpeg-dev gcc python3-dev musl-dev
# RUN apk add libc-dev libffi-dev

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY /sweetrecipe /sweetrecipe/

CMD python3 manage.py runserver 0.0.0.0:8000