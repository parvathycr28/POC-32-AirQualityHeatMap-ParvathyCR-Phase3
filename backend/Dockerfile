FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/data ./data
COPY assistant ./assistant

COPY data-science/outputs/intelligence_results.json ./data-science/outputs/intelligence_results.json
COPY data-science/outputs/intelligence_summary.json ./data-science/outputs/intelligence_summary.json

ENV INTELLIGENCE_RESULTS_FILE=/app/data-science/outputs/intelligence_results.json
ENV INTELLIGENCE_SUMMARY_FILE=/app/data-science/outputs/intelligence_summary.json

EXPOSE 8000 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]