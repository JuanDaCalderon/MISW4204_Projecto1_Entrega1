FROM python:3.9

WORKDIR /app

COPY . /app

COPY nube-4204-565a35f26b70.json /app/nube-4204-565a35f26b70.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/nube-4204-565a35f26b70.json

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "push.py"]
