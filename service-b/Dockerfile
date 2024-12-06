# service-b/Dockerfile

FROM python:3.8-slim
COPY app.py /app.py
RUN pip install boto3 aws-xray-sdk
CMD ["python", "/app.py"]
