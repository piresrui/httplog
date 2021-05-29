FROM python:3.8

ENV PYTHONUNBUFFERED=1

RUN mkdir /app
ADD . /app
WORKDIR /app

RUN make test
RUN make install

CMD ["httplog"]
