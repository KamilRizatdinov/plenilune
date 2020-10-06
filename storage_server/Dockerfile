FROM python:3.7-slim
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /storage
COPY ./ /storage
EXPOSE 8000
CMD ["python", "storage.py"]