FROM python:3.11-slim
WORKDIR /Api_Rest
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD bash -c "python3 Api_Rest.py; exec bash"