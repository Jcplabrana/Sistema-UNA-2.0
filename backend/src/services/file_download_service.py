import os
import re
import logging
import requests
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def download_file(url, download_folder):
    if not url or not url.split('/')[-1].split('.')[-1].lower() in ['pdf', 'zip', 'rar', '7z', 'docx']:
        logging.info(f"URL ignorada ou formato não suportado: {url}")
        return None
    local_filename = os.path.join(download_folder, sanitize_filename(url.split('/')[-1]))
    if os.path.exists(local_filename):
        logging.info(f"Arquivo duplicado: {local_filename}")
        return local_filename

    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("http://", adapter)
    http.mount("https://", adapter)

    try:
        with http.get(url, stream=True, timeout=10, verify=False) as response:
            response.raise_for_status()
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KiloByte
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True,
                                desc=f"Baixando {os.path.basename(local_filename)}")
            with open(local_filename, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                logging.error("Erro no download: Tamanho do arquivo baixado não corresponde ao esperado.")
                return None
        logging.info(f"Download concluído: {local_filename}")
        return local_filename
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao baixar o arquivo {url} com requests: {e}")
        return alternative_download_file(url, download_folder)

import urllib.request

def alternative_download_file(url, download_folder):
    local_filename = os.path.join(download_folder, sanitize_filename(url.split('/')[-1]))
    try:
        with urllib.request.urlopen(url) as response:
            with open(local_filename, 'wb') as out_file:
                out_file.write(response.read())
        logging.info(f"Download alternativo concluído: {local_filename}")
        return local_filename
    except Exception as e:
        logging.error(f"Erro no download alternativo do arquivo {url}: {e}")
        return None
