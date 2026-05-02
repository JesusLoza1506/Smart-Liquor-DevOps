# 1. Imagen base estable
FROM python:3.10-slim

# 2. Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Directorio de trabajo
WORKDIR /app

# 4. Dependencias del sistema (optimizadas en una sola capa)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalación de librerías (Usando caché de capas)
# Solo se volverá a ejecutar si cambias el requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copia del código (Gracias al .dockerignore, esto será instantáneo)
COPY . .

# 7. Ahora solo necesitamos el puerto 8000 para el Monolito (API + Web)
EXPOSE 8000

# 8. Comando de arranque
CMD ["python", "app/main.py"]