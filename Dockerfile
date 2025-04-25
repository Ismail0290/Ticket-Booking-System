FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations and start server
CMD ["gunicorn", "ticket_booking.wsgi:application", "--bind", "0.0.0.0:8000"]
