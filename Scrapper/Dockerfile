FROM python:3.11-slim
WORKDIR /Scrapper
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD bash -c "python3 Web_Scrapper.py; exec bash"