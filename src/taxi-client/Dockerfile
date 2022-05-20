FROM python:latest
WORKDIR /usr/app/taxi-client
COPY TaxiLocationPublisher.py requirements.txt ./

RUN pip install -r requirements.txt
CMD ["python","TaxiLocationPublisher.py"]