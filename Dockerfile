FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install --with-deps

CMD ["python", "main.py"]
