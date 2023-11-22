# Usa una imagen base de Python
FROM python:3.9
  

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido de la aplicación en el contenedor
COPY . /app

# Copia el archivo de requisitos e instala las dependencias
RUN pip install -r requirements.txt


# Expone el puerto en el que se ejecutará la aplicación Flask
EXPOSE 5001

# Ejecuta la aplicación Flask
CMD ["python", "api.py"]