# Use Python 3.11
FROM python:3.11

# Set working directory
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY *.py .

EXPOSE 8000
CMD ["python", "main.py"]