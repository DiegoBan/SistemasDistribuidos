FROM python:3.11-slim
WORKDIR /Generador_de_Trafico
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD bash -c "python3 Insertar_Cache.py; exec bash"