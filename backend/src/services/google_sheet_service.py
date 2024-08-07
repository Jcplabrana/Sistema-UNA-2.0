import logging
from config.config import sheets_service

def update_google_sheet(data, spreadsheet_id, sheet_names):
    try:
        for sheet_name in sheet_names:
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=sheet_name).execute()
            num_rows = len(result.get('values', []))
            range_name = f'{sheet_name}!A{num_rows + 1}'

            body = {
                'values': data
            }

            sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            logging.info(f"Dados atualizados na aba {sheet_name} da planilha do Google Sheets com ID: {spreadsheet_id}")
    except Exception as e:
        logging.error(f"Erro ao atualizar a planilha do Google Sheets: {e}")
