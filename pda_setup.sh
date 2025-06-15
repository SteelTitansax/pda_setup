#!/bin/bash

echo "=== Instalando entorno PDA ==="

# Actualizar paquetes
apt update && apt upgrade -y

# Instalar herramientas básicas + cmatrix
apt install -y python3 python3-pip curl ssh npm ffmpeg tesseract-ocr poppler-utils git build-essential libgl1 cmatrix

# Actualizar pip y crear directorios
pip install --upgrade pip setuptools wheel
mkdir -p ~/pda_project/pda_output
cd ~/pda_project || exit

# Instalar librerías Python requeridas
pip install Flask pytesseract pdf2image Pillow docx2txt textract beautifulsoup4 ebooklib deep-translator gTTS pydub whisper openai-whisper torch textwrap3 bs4

# Crear archivo principal del menú (igual que antes)
cat > menu.py << 'EOF'
import os
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import docx2txt
import textract
from gtts import gTTS
from deep_translator import GoogleTranslator
import whisper

os.makedirs("pda_output", exist_ok=True)

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def pause():
    input("\nPresiona ENTER para continuar...")

def pdf_to_text(path):
    images = convert_from_path(path)
    text = ''
    for i, image in enumerate(images):
        temp = f"pda_output/page_{i}.png"
        image.save(temp, 'PNG')
        text += pytesseract.image_to_string(Image.open(temp)) + "\n"
    return text

def docx_to_text(path):
    return docx2txt.process(path)

def file_to_text(path):
    if path.endswith(".pdf"):
        return pdf_to_text(path)
    elif path.endswith(".docx"):
        return docx_to_text(path)
    else:
        return textract.process(path).decode()

def image_to_text(path):
    return pytesseract.image_to_string(Image.open(path))

def text_to_audio(text, filename="output.mp3", lang="es"):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(f"pda_output/{filename}")
        print(f">>> Audio guardado: pda_output/{filename}")
    except ValueError:
        print(">>> Idioma no válido o texto vacío.")

def audio_to_text(path, lang=None):
    model = whisper.load_model("base")
    result = model.transcribe(path, language=lang)
    return result['text']

def translate_text(text, target='en'):
    return GoogleTranslator(source='auto', target=target).translate(text)

def save_text(text, name="output.txt"):
    path = Path(f"pda_output/{name}")
    path.write_text(text, encoding='utf-8')
    print(f">>> Texto guardado en: {path}")

def main():
    while True:
        clear()
        print("=== PDA CONVERSOR TUI ===\n")
        print("1. Archivo a texto (PDF, DOCX, TXT)")
        print("2. Imagen a texto (OCR)")
        print("3. Texto a audio (TTS multilenguaje)")
        print("4. Traducir texto")
        print("5. Audio a texto (Whisper multilenguaje)")
        print("6. Mostrar efecto
