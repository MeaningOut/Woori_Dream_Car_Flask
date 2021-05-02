FROM python:3.8.5
COPY . /app
WORKDIR /app
RUN apt-get update
COPY requirements.txt /app
RUN pip install -r requirements.txt
ENTRYPOINT ["flask"]
CMD ["run", "--host", "0.0.0.0"]
