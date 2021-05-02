FROM ubuntu:latest
COPY . /app
WORKDIR /app
RUN apt-get update
RUN apt-get install -y python3.8 python3-pip --fix-missing
COPY requirements.txt /app
RUN pip install -r requirements.txt
ENTRYPOINT ["flask"]
CMD ["run", "--host", "0.0.0.0"]
