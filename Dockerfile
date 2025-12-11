FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para cliente MySQL si fuera necesario
# (mysql-connector-python es puro python, pero a veces se necesitan librerias base)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
