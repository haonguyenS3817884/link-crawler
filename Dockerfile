FROM python:3.11-slim

WORKDIR /app

COPY requirements/prod.txt ./requirements/prod.txt
RUN pip install --no-cache-dir -r ./requirements/prod.txt
RUN playwright install --with-deps

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]