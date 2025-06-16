import os
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import docx2txt
import textract
from gtts import gTTS
from deep_translator import GoogleTranslator
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
import textwrap
from pydub import AudioSegment
import subprocess
import shutil

INPUT_DIR = Path("pda_input")
OUTPUT_DIR = Path("pda_output")

OUTPUT_DIR.mkdir(exist_ok=True)
INPUT_DIR.mkdir(exist_ok=True)

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

def pause():
    input("\nPresiona ENTER para continuar...")

def pdf_to_text(path):
    images = convert_from_path(path)
    text = ''
    for i, image in enumerate(images):
        temp = OUTPUT_DIR / f"page_{i}.png"
        image.save(temp, 'PNG')
        text += pytesseract.image_to_string(Image.open(temp)) + "\n"
    return text

def docx_to_text(path):
    return docx2txt.process(path)

def epub_to_text(path):
    text = ""
    book = epub.read_epub(path)
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text() + "\n"
    return text

def file_to_text(path):
    if path.endswith(".pdf"):
        return pdf_to_text(path)
    elif path.endswith(".docx"):
        return docx_to_text(path)
    elif path.endswith(".epub"):
        return epub_to_text(path)
    else:
        return textract.process(path).decode()

def image_to_text(path):
    return pytesseract.image_to_string(Image.open(path))

def text_to_audio(text, filename="output.mp3", lang="es"):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(OUTPUT_DIR / filename)
        print(f">>> Audio guardado: {OUTPUT_DIR / filename}")
    except ValueError:
        print(">>> Idioma no válido o texto vacío.")

def get_next_part(base_name):
    i = 1
    while os.path.exists(f"{base_name}_part_{i}.mp3"):
        i += 1
    return i

def text_to_audio_in_volumes(text_input, text_output="output.mp3", lang="es", max_words=5000):
    input_path = INPUT_DIR / text_input
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = textwrap.wrap(text, 4000)
    output_base = str(input_path).replace(".txt", "")
    next_part = get_next_part(output_base)

    generated_files = []  # Para guardar la lista de MP3s generados

    for i, chunk in enumerate(chunks):
        tts = gTTS(text=chunk, lang=lang, slow=False)
        output_file = f"{output_base}_part_{next_part + i}.mp3"
        tts.save(output_file)
        generated_files.append(output_file)
        print(f"Audio guardado: {output_file}")

    # Consolidar todos los archivos generados en uno solo
    consolidated_audio = AudioSegment.empty()
    for mp3_file in generated_files:
        consolidated_audio += AudioSegment.from_mp3(mp3_file)

    # Guardar el archivo final consolidado en OUTPUT_DIR
    output_path = OUTPUT_DIR / text_output
    consolidated_audio.export(output_path, format="mp3")
    print(f">>> Audio consolidado guardado en: {output_path}")

    # Borrar los archivos de partes temporales
    for mp3_file in generated_files:
        os.remove(mp3_file)
        print(f"Archivo temporal eliminado: {mp3_file}")

    # Eliminar el archivo de texto original
    os.remove(INPUT_DIR / text_input)
    print(f"Archivo de texto eliminado: {text_input}")

def translate_text(text, target='en'):
    return GoogleTranslator(source='auto', target=target).translate(text)

def translate_text_in_chunks(text, target='en', chunk_size=5000):
    chunks = textwrap.wrap(text, chunk_size)
    translated_chunks = []
    temp_files = []

    for i, chunk in enumerate(chunks):
        print(f"Traduciendo chunk {i+1} de {len(chunks)}...")
        translated_chunk = translate_text(chunk, target)
        temp_file_path = OUTPUT_DIR / f"translated_chunk_{i+1}.txt"
        temp_file_path.write_text(translated_chunk, encoding='utf-8')
        temp_files.append(temp_file_path)

    final_text = ""
    for temp_path in temp_files:
        final_text += temp_path.read_text(encoding='utf-8') + "\n"
        temp_path.unlink()  # Borrar chunk temporal

    return final_text

def save_text_in_volumes(text, base_name, max_words=20000):
    words = text.split()
    total_words = len(words)
    volumes = (total_words // max_words) + (1 if total_words % max_words > 0 else 0)

    for i in range(volumes):
        start = i * max_words
        end = start + max_words
        volume_words = words[start:end]
        volume_text = " ".join(volume_words)
        volume_name = f"{Path(base_name).stem}_volume_{i+1}.txt"
        path = INPUT_DIR / volume_name
        path.write_text(volume_text, encoding='utf-8')
        print(f">>> Texto guardado en: {path}")

def save_text(text, name):
    output_name = Path(name).stem + ".txt"
    path = INPUT_DIR / output_name
    path.write_text(text, encoding='utf-8')
    print(f">>> Texto guardado en: {path}")

def move_files(src_dir, dest_dir):
    for file_path in src_dir.iterdir():
        if file_path.is_file():
            shutil.move(str(file_path), dest_dir / file_path.name)
    print(f">>> Archivos movidos de {src_dir} a {dest_dir}")

def clear_directory(directory):
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_path.unlink()
    print(f">>> Todos los archivos de {directory} han sido eliminados.")

def main():
    while True:
        clear_console()
        print("=== PDA CONVERSOR TUI ===\n")
        print("1. Archivo a texto (PDF, DOCX, EPUB, TXT)")
        print("2. Imagen a texto (OCR)")
        print("3. Texto a audio (TTS multilenguaje)")
        print("4. Traducir texto desde archivo")
        print("5. Iniciar servidor http para transferencia de archivos PDA")
        print("6. Mover archivos de 'pda_output' a 'pda_input'")
        print("7. Mover archivos de 'pda_input' a 'pda_output'")
        print("8. Borrar todos los archivos de 'pda_input'")
        print("9. Borrar todos los archivos de 'pda_output'")
        print("10. Salir")
        choice = input("\nSelecciona una opción: ")

        if choice == '1':
            filename = input("Nombre del archivo (PDF/DOCX/EPUB/TXT) en 'input/': ")
            path = INPUT_DIR / filename
            if not path.exists():
                print(">>> Archivo no encontrado en la carpeta 'input'.")
                pause()
                continue
            text = file_to_text(str(path))
            print("\n>>> TEXTO EXTRAÍDO:\n")
            print(text[:1000] + "\n...")

            word_count = len(text.split())
            if word_count > 20000:
                print(f"El texto tiene {word_count} palabras, se dividirá en volúmenes de 20000 palabras.")
                save_text_in_volumes(text, filename, max_words=20000)
            else:
                save_text(text, filename)
            pause()

        elif choice == '2':
            filename = input("Nombre de la imagen (JPG/PNG) en 'input/': ")
            path = INPUT_DIR / filename
            if not path.exists():
                print(">>> Imagen no encontrada en 'input'.")
                pause()
                continue
            text = image_to_text(str(path))
            print("\n>>> TEXTO OCR:\n")
            print(text)
            save_text(text, f"{filename.split('.')[0]}.txt")
            pause()

        elif choice == '3':
            text_input = input("Texto a convertir a voz: ")
            text_output = input("Nombre del archivo de audio (output.mp3): ") or "output.mp3"
            lang = input("Idioma (ej: es, en, fr, de): ") or "es"

            print(f"Procesando {text_input}. Dividiendo en volumenes ... ")
            text_to_audio_in_volumes(text_input, text_output, lang, max_words=5000)

            pause()

        elif choice == '4':
            filename = input("Nombre del archivo de texto en 'input/': ")
            path = INPUT_DIR / filename
            lang = input("Idioma destino (ej: en, es, fr): ")
            if not path.exists():
                print(">>> Archivo no encontrado en 'input'.")
                pause()
                continue

            try:
                text = path.read_text(encoding='utf-8')
                if text:
                    if len(text) > 5000:
                        print("El texto supera los 5000 caracteres. Aplicando división en chunks...")
                        translated = translate_text_in_chunks(text, lang)
                    else:
                        translated = translate_text(text, lang)

                    print(f"\n>>> TEXTO TRADUCIDO [{lang}]:\n{translated[:1000]}...\n")
                    save_text(translated, f"{filename.split('.')[0]}_translated_{lang}.txt")
                else:
                    print("El archivo está vacío.")
            except Exception as e:
                print(f"Ocurrió un error: {e}")

            pause()

        elif choice == '5':
            print("Iniciando servidor Flask en http://0.0.0.0:8080 ... (CTRL+C para detener)")
            try:
                subprocess.run(['python3', 'pda_http_server.py'])
            except Exception as e:
                print(f"Error al iniciar el servidor Flask: {e}")
            pause()

        elif choice == '6':
            move_files(OUTPUT_DIR, INPUT_DIR)
            pause()

        elif choice == '7':
            move_files(INPUT_DIR, OUTPUT_DIR)
            pause()

        elif choice == '8':
            clear_directory(INPUT_DIR)
            pause()

        elif choice == '9':
            clear_directory(OUTPUT_DIR)
            pause()

        elif choice == '10':
            print("Saliendo del programa.")
            break

        else:
            print("Opción inválida.")
            pause()

if __name__ == "__main__":
    main()
  
