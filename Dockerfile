FROM python:3.14-slim

# Создать непривилегированного пользователя
RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем только пакет приложения
COPY dominus dominus

# Дать права на рабочую директорию
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "dominus.main:app", "--host", "0.0.0.0", "--port", "8000"] 
