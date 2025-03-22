FROM python:3.9
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && pip freeze > installed.txt
COPY . /app/
EXPOSE 8000
CMD ["uvicorn", "web-api:app", "--host", "0.0.0.0", "--port", "8000"]
