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
        print(">>> Idioma no valido o texto vacio.")

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
        print("6. Salir")
        choice = input("\nSelecciona una opcion: ")

        if choice == '1':
            path = input("Ruta del archivo (PDF/DOCX/TXT): ")
            text = file_to_text(path)
            print("\n>>> TEXTO EXTRAIDO:\n")
            print(text[:1000] + "\n...")
            save_text(text)
            pause()

        elif choice == '2':
            path = input("Ruta de la imagen (JPG/PNG): ")
            text = image_to_text(path)
            print("\n>>> TEXTO OCR:\n")
            print(text)
            save_text(text, "ocr_output.txt")
            pause()

        elif choice == '3':
            text = input("Texto a convertir a voz: ")
            filename = input("Nombre del archivo de audio (output.mp3): ") or "output.mp3"
            lang = input("Idioma (ej: es, en, fr, de): ") or "es"
            text_to_audio(text, filename, lang)
            pause()

        elif choice == '4':
            text = input("Texto a traducir: ")
            lang = input("Idioma destino (ej: en, es, fr): ")
            translated = translate_text(text, lang)
            print(f"\n>>> TEXTO TRADUCIDO [{lang}]:\n{translated}")
            save_text(translated, f"translated_{lang}.txt")
            pause()

        elif choice == '5':
            path = input("Ruta del archivo de audio/video: ")
            lang = input("Codigo del idioma (opcional, ej: en, es, fr): ") or None
            print("Procesando audio, esto puede tardar...")
            text = audio_to_text(path, lang)
            print("\n>>> TRANSCRIPCION:\n")
            print(text)
            save_text(text, "transcripcion.txt")
            pause()

        elif choice == '6':
            break

        else:
            print("Opcion invalida.")
            pause()

if __name__ == "__main__":
    main()
