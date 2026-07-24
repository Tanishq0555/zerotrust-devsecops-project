FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Created non-root user and switch to it
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 3000

CMD ["python", "app.py"]

