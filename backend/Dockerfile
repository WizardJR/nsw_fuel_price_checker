
FROM python:3.11.9

WORKDIR /app

COPY backend/ /app/backend/

RUN pip install --no-cache-dir -r /app/backend/requirements.txt

EXPOSE 8010

CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8010"]