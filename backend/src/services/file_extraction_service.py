import os
import logging
import zipfile
import rarfile
import py7zr
import threading

from backend.src.services.file_download_service import sanitize_filename

arquivos_com_erros = []

def extract_files(file_path, extract_folder):
    try:
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
        elif rarfile.is_rarfile(file_path):
            with rarfile.RarFile(file_path, 'r') as rar_ref:
                rar_ref.extractall(extract_folder)
        elif file_path.endswith('.7z'):
            with py7zr.SevenZipFile(file_path, mode='r') as seven_z:
                seven_z.extractall(extract_folder)
        logging.info(f"Extração concluída: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Erro ao extrair o arquivo {file_path}: {e}")
        arquivos_com_erros.append(os.path.basename(file_path))
        return False

def extract_files_with_timeout(file_path, extract_folder, timeout=300):
    def target():
        return extract_files(file_path, extract_folder)

    result = [False]
    thread = threading.Thread(target=lambda: result.append(target()))
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        logging.error(f"Timeout ao extrair o arquivo {file_path}")
        thread.join()
        arquivos_com_erros.append(os.path.basename(file_path))
        return False
    return result[-1]

def process_nested_archives(extract_folder, timeout):
    nested_archives = [os.path.join(extract_folder, f) for f in os.listdir(extract_folder) if
                       f.endswith(('.zip', '.rar', '.7z'))]
    while nested_archives:
        archive = nested_archives.pop()
        logging.info(f"Extraindo arquivo aninhado: {archive}")
        nested_extract_folder = os.path.join(extract_folder, sanitize_filename(os.path.splitext(os.path.basename(archive))[0]))
        os.makedirs(nested_extract_folder, exist_ok=True)
        if extract_files_with_timeout(archive, nested_extract_folder, timeout):
            os.remove(archive)
            new_nested_archives = [os.path.join(nested_extract_folder, f) for f in os.listdir(nested_extract_folder) if
                                   f.endswith(('.zip', '.rar', '.7z'))]
            nested_archives.extend(new_nested_archives)
