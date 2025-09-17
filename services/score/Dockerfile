FROM python:3.11-slim
WORKDIR /app
COPY ./services/score /app
COPY ./shared /app/shared
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
