# service-a/Dockerfile

FROM python:3.8-slim
COPY app.py /app.py
RUN pip install boto3
CMD ["python", "/app.py"]
