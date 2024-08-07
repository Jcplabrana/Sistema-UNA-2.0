import os
import logging
from googleapiclient.http import MediaFileUpload
from config.config import drive_service

def file_exists_in_gdrive(file_name, folder_id):
    query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
    try:
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        if items:
            logging.info(f"Arquivo {file_name} já existe no Google Drive com ID: {items[0]['id']}")
            return items[0]['id']
        else:
            return None
    except Exception as e:
        logging.error(f"Erro ao verificar a existência do arquivo {file_name} no Google Drive: {e}")
        return None

def upload_file_to_gdrive(file_path, folder_id):
    file_name = os.path.basename(file_path)
    existing_file_id = file_exists_in_gdrive(file_name, folder_id)
    if existing_file_id:
        logging.info(f"Arquivo {file_path} já existe no Google Drive com ID: {existing_file_id}")
        webViewLink = f"https://drive.google.com/file/d/{existing_file_id}/view?usp=sharing"
        ensure_public_permissions(existing_file_id)
        return existing_file_id, webViewLink

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    try:
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        logging.info(f"Arquivo {file_path} carregado com sucesso no Google Drive com ID: {file.get('id')}")
        file_id = file.get('id')
        ensure_public_permissions(file_id)
        webViewLink = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        return file_id, webViewLink
    except Exception as e:
        logging.error(f"Erro ao carregar {file_path} no Google Drive: {e}")
        return None, None

def ensure_public_permissions(file_id):
    try:
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        drive_service.permissions().create(fileId=file_id, body=permission).execute()
        logging.info(f"Permissões públicas configuradas para o arquivo com ID: {file_id}")
    except Exception as e:
        logging.error(f"Erro ao configurar permissões públicas para o arquivo com ID: {file_id}: {e}")

def convert_docx_to_gdoc(file_id):
    try:
        file_metadata = {
            'name': 'converted_document',
            'mimeType': 'application/vnd.google-apps.document'
        }
        converted = drive_service.files().copy(fileId=file_id, body=file_metadata).execute()
        logging.info(f"Arquivo convertido para Google Docs com ID: {converted.get('id')}")
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        drive_service.permissions().create(fileId=converted.get('id'), body=permission).execute()
        return converted.get('id'), converted.get('webViewLink')
    except Exception as e:
        logging.error(f"Erro ao converter DOCX para Google Docs: {e}")
        return None, None
