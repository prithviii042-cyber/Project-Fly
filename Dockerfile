FROM python:3.11-slim

# Set working directory to the backend so run.py can be called directly
WORKDIR /app/backend

# Install dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

EXPOSE 5001

CMD ["python", "run.py"]
