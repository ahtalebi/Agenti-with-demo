#!/bin/bash
# install-packages.sh

echo "Installing core "
pip install --no-cache-dir fastapi==0.103.1 uvicorn==0.23.2 python-dotenv==1.0.0 python-multipart==0.0.6

echo 
pip install --no-cache-dir langchain==0.3.25 langchain-community==0.3.7 langchain-openai==0.3.16 chromadb==0.6.3

echo "Installing document processing "
pip install --no-cache-dir PyPDF2==3.0.1 numpy==1.26.0 pandas==2.2.0 python-docx==1.1.0 openpyxl==3.1.2

echo "done"
