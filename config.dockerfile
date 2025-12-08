# Este archivo es para cumplir el requisito de "Contenerización"
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Este comando es demostrativo
CMD ["python", "main.py"]