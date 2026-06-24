FROM python:3.12-slim

WORKDIR /app

# Copy shared library first so it can be installed as a package
COPY shared/ ./shared/

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/main.py ./main.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
