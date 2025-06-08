FROM python:3.8.8-slim

# نصب کتابخانه‌های سیستمی موردنیاز opencv و ابزارهای پایه
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy all app files
COPY . .

# پیش‌فرض کاری انجام نمیده. فرمان اجرایی در docker-compose مشخص می‌شود.
CMD ["sleep", "infinity"]