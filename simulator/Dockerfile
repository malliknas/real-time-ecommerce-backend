FROM python:3.10-slim

WORKDIR /app

# Install netcat-openbsd (instead of the virtual 'netcat')
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x wait-for-kafka.sh

CMD ["./wait-for-kafka.sh"]
