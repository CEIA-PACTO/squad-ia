#!/bin/bash

# Inicia FastAPI em background
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# Inicia Streamlit no foreground (mantém o container vivo)
streamlit run src/app.py --server.port=8501 --server.enableCORS=false
