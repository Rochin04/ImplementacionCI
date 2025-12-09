FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código Y la base de datos (si existe en la carpeta)
COPY . .

# Exponer el puerto que usas en docker-compose
EXPOSE 5000

# Usar uvicorn para correr la app en el puerto 5000 y host 0.0.0.0
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
