import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = r'G:\Programador JC\automacaomake-424118-f166235a4ab7.json'
FOLDER_ID = '1UYmFFCNfVR9HhfJpoOQWfHtyXm-XCzC8'
PDF_FOLDER_ID = '1VEdirHLWrU98I7viFEV7bUtGzUfRTPkD'
SPREADSHEET_ID = '1PEoLUkDpfKhPf6c4w_lcgjpbly9L3TrL3mWDHW1obhs'
SHEET_NAMES = ['Licitações a Verificar - Versão 2.0 Sistema', 'Sistema UNA - Versão 2.0']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)
