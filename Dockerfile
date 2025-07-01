FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y wget gnupg ca-certificates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps

COPY . .

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
