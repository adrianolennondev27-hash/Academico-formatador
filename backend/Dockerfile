FROM python:3.11-slim

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Instala dependências de sistema:
# - LibreOffice (conversão DOCX ↔ PDF ↔ ODT)
# - Tesseract + pacote PT-BR (OCR de PDFs escaneados)
# - Poppler (extração de imagens de PDF)
# - Fonts (Arial / Times / Courier — Microsoft core fonts)
# - libgl1 (necessário pro OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-writer \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    libgl1 \
    fontconfig \
    cabextract \
    wget \
    && echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections \
    && apt-get install -y --no-install-recommends ttf-mscorefonts-installer \
    && fc-cache -f -v \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]