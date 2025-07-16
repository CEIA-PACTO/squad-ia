FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y curl && apt-get clean

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000 8501

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
