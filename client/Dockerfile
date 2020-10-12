FROM python:3.7-slim
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /client
COPY ./ /client
EXPOSE 8000
