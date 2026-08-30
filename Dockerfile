FROM python:3.11-slim

WORKDIR /app

# Memory optimizations for Free Tier limits (512MB)
ENV MALLOC_ARENA_MAX=2
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV WEB_CONCURRENCY=1
ENV PYTHONUNBUFFERED=1

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model files
COPY . .

# Uncompress the model during build (where we have more RAM) to allow true memory mapping in production
RUN python -c "import joblib; model=joblib.load('dataco_rf_model.joblib'); joblib.dump(model, 'dataco_rf_model_uncompressed.joblib', compress=0)"

# Render.com uses port 10000 by default
EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1", "--limit-concurrency", "50"]
