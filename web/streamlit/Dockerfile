FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit pandas matplotlib

COPY web/streamlit/ /app/web/streamlit/
COPY web/api/utils/ /app/web/api/utils/
COPY src/utils/ /app/src/utils/
COPY config.yaml /app/

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["streamlit", "run", "web/streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

