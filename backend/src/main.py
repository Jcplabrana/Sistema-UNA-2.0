import os
import logging
import pandas as pd
from tqdm import tqdm
from services.html_extraction_service import extract_data_from_html
from services.file_download_service import download_file, alternative_download_file
from services.google_drive_service import upload_file_to_gdrive, file_exists_in_gdrive, ensure_public_permissions, convert_docx_to_gdoc
from services.pdf_processing_service import process_all_pdfs, process_pdf, merge_pdfs
from services.google_sheet_service import update_google_sheet
from utils.file_utils import sanitize_filename
from utils.filter_utils import apply_filters
from config.config import SPREADSHEET_ID, SHEET_NAMES, PDF_FOLDER_ID, FOLDER_ID
import logging_config
import socket

# Lista para registrar arquivos com erros
arquivos_com_erros = []

def extract_files(file_path, extract_folder):
    import zipfile
    import rarfile
    import py7zr

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
    import threading

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

def check_connection():
    try:
        socket.create_connection(("www.googleapis.com", 80))
        return True
    except OSError:
        return False

def process_licitacoes(directory_path, download_folder):
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.html')]
    all_data = []
    for file_path in tqdm(file_paths, desc="Processando arquivos HTML"):
        all_data.extend(extract_data_from_html(file_path))

    df_all = pd.DataFrame(all_data)
    filtered_df = apply_filters(df_all)

    filtered_output_file = os.path.join(directory_path, 'filtered_data.xlsx')
    try:
        filtered_df.to_excel(filtered_output_file, index=False)
        logging.info(f"Planilha com informações dos editais salvos em: {filtered_output_file}")
    except PermissionError:
        filtered_output_file = os.path.join(download_folder, 'filtered_data.xlsx')
        filtered_df.to_excel(filtered_output_file, index=False)
        logging.info(f"Planilha com informações dos editais salvos em: {filtered_output_file}")

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    pdf_unidos_folder = os.path.join(download_folder, 'Pdf Unidos')
    docx_folder = os.path.join(download_folder, 'Docx Convertidos')
    if not os.path.exists(pdf_unidos_folder):
        os.makedirs(pdf_unidos_folder)
    if not os.path.exists(docx_folder):
        os.makedirs(docx_folder)

    filtered_df['Link PDF Google Drive'] = ""
    filtered_df['Link DOCX Google Drive'] = ""
    filtered_df['Link Google Docs'] = ""
    filtered_df['ID Google Docs'] = ""
    filtered_df['Arquivo de Origem'] = ""

    for idx, row in tqdm(filtered_df.iterrows(), total=filtered_df.shape[0], desc="Baixando arquivos"):
        if row['Acesso']:
            download_path = download_file(row['Acesso'], download_folder)
            if download_path and isinstance(download_path, str) and os.path.exists(download_path):
                filtered_df.at[idx, 'Arquivo Baixado'] = download_path
            else:
                logging.error(f"Falha no download do arquivo: {row['Acesso']}")

    for idx, row in tqdm(filtered_df.iterrows(), total=filtered_df.shape[0], desc="Descompactando e unindo PDFs"):
        download_path = row.get('Arquivo Baixado', None)
        if download_path and isinstance(download_path, str) and os.path.exists(download_path):
            if download_path.endswith(('.zip', '.rar', '.7z')):
                extract_folder = os.path.join(download_folder, sanitize_filename(
                    os.path.splitext(os.path.basename(download_path))[0]))
                os.makedirs(extract_folder, exist_ok=True)
                if extract_files_with_timeout(download_path, extract_folder):
                    process_nested_archives(extract_folder, timeout=300)
                merged_pdf_path = merge_pdfs(extract_folder, pdf_unidos_folder, sanitize_filename(
                    os.path.splitext(os.path.basename(download_path))[0]))
                if merged_pdf_path:
                    filtered_df.at[idx, 'Arquivo Baixado'] = merged_pdf_path
                else:
                    filtered_df.at[idx, 'Arquivo Baixado'] = download_path

    for pdf_path in tqdm([row.get('Arquivo Baixado') for _, row in filtered_df.iterrows() if isinstance(row.get('Arquivo Baixado'), str) and row.get('Arquivo Baixado').endswith('.pdf')], desc="Convertendo PDFs para DOCX"):
        docx_path = os.path.join(docx_folder, os.path.splitext(os.path.basename(pdf_path))[0] + '.docx')
        if not os.path.exists(docx_path):
            docx_path = process_pdf(pdf_path, docx_folder)
        else:
            logging.info(f"O arquivo {docx_path} já foi convertido. Pulando conversão.")

        if os.path.exists(docx_path):
            filtered_df.loc[filtered_df['Arquivo Baixado'] == pdf_path, 'Arquivo DOCX'] = docx_path

    for idx, row in filtered_df.iterrows():
        pdf_path = row.get('Arquivo Baixado')
        if isinstance(pdf_path, str) and pdf_path.endswith('.pdf'):
            docx_path = os.path.join(docx_folder, os.path.splitext(os.path.basename(pdf_path))[0] + '.docx')
            if os.path.exists(docx_path):
                filtered_df.at[idx, 'Arquivo DOCX'] = docx_path
            else:
                logging.error(f"Falha na conversão de PDF para DOCX: {pdf_path}")

    if check_connection():
        pdf_files = [row.get('Arquivo Baixado', None) for idx, row in filtered_df.iterrows() if
                     isinstance(row.get('Arquivo Baixado', None), str) and row['Arquivo Baixado'].endswith('.pdf')]
        for pdf_path in tqdm(pdf_files, total=len(pdf_files), desc="Carregando PDFs para Google Drive"):
            if pdf_path:
                if not file_exists_in_gdrive(os.path.basename(pdf_path), PDF_FOLDER_ID):
                    file_id, webViewLink = upload_file_to_gdrive(pdf_path, PDF_FOLDER_ID)
                    if webViewLink:
                        filtered_df.loc[filtered_df['Arquivo Baixado'] == pdf_path, 'Link PDF Google Drive'] = webViewLink
                else:
                    logging.info(f"O arquivo {pdf_path} já existe no Google Drive. Pulando upload.")
                    file_id = file_exists_in_gdrive(os.path.basename(pdf_path), PDF_FOLDER_ID)
                    webViewLink = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
                    filtered_df.loc[filtered_df['Arquivo Baixado'] == pdf_path, 'Link PDF Google Drive'] = webViewLink

        docx_files = [os.path.join(docx_folder, f) for f in os.listdir(docx_folder) if f.endswith('.docx')]
        for docx_path in tqdm(docx_files, total=len(docx_files), desc="Carregando DOCX para Google Drive"):
            if not file_exists_in_gdrive(os.path.basename(docx_path), FOLDER_ID):
                file_id, webViewLink = upload_file_to_gdrive(docx_path, FOLDER_ID)
                if webViewLink:
                    filtered_df.loc[filtered_df['Arquivo DOCX'] == docx_path, 'Link DOCX Google Drive'] = webViewLink
                    gdoc_id, gdoc_link = convert_docx_to_gdoc(file_id)
                    if gdoc_link:
                        filtered_df.loc[filtered_df['Arquivo DOCX'] == docx_path, 'Link Google Docs'] = gdoc_link
                        filtered_df.loc[filtered_df['Arquivo DOCX'] == docx_path, 'ID Google Docs'] = gdoc_id
            else:
                logging.info(f"O arquivo {docx_path} já existe no Google Drive. Pulando upload.")
                file_id = file_exists_in_gdrive(os.path.basename(docx_path), FOLDER_ID)
                webViewLink = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
                filtered_df.loc[filtered_df['Arquivo DOCX'] == docx_path, 'Link DOCX Google Drive'] = webViewLink
                gdoc_id, gdoc_link = convert_docx_to_gdoc(file_id)
                if gdoc_link:
                    filtered_df.loc[filtered_df['Arquivo DOCX'] == docx_path, 'Link Google Docs'] = gdoc_link
                    filtered_df.loc[filtered_df['Arquivo DOCX'] == docx_path, 'ID Google Docs'] = gdoc_id

        filtered_df = filtered_df[
            ['Prazo Abertura', 'Objeto', 'Modalidade', 'N Licitação', 'Valor Edital', 'UASG', 'Órgão Licitante',
             'Prazo (Hora)', 'Cidade', 'UF', 'Acesso', 'Observações', 'Link PDF Google Drive', 'Link DOCX Google Drive', 'Link Google Docs', 'ID Google Docs', 'Arquivo de Origem']]

        data = filtered_df.values.tolist()
        data = [[str(cell) if pd.notna(cell) else "" for cell in row] for row in data]
        update_google_sheet(data, SPREADSHEET_ID, SHEET_NAMES)

    summary = {
        "Total de itens antes do filtro": len(df_all),
        "Total de itens filtrados": len(df_all) - len(filtered_df),
        "Total de itens restantes": len(filtered_df)
    }

    if arquivos_com_erros:
        logging.info("Arquivos que precisam de revisão:")
        for arquivo in arquivos_com_erros:
            logging.info(arquivo)

    return summary, filtered_output_file

if __name__ == "__main__":
    import sys
    directory_path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\jcpla\Desktop\Licitações\Meses\Julho\Dia 22\Arquivos Email'
    download_folder = sys.argv[2] if len(sys.argv) > 2 else r'C:\Users\jcpla\Desktop\Licitações\Meses\Julho\Dia 22\Downloads'
    summary, output_file = process_licitacoes(directory_path, download_folder)
    logging.info(summary)
    if output_file:
        logging.info(f"Dados filtrados salvos em {output_file}")
