import os
import logging
import pikepdf
from PyPDF2 import PdfReader, PdfWriter
from pdf2docx import Converter
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def optimize_pdf(input_path, output_path):
    try:
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path)
        logging.info(f"Otimizado {input_path} e salvo em {output_path}")
    except Exception as e:
        logging.error(f"Erro ao otimizar {input_path}: {e}")

def clean_pdf(input_path, output_path):
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            if '/Annots' in page:
                page.pop('/Annots')
            writer.add_page(page)

        with open(output_path, 'wb') as f:
            writer.write(f)
        logging.info(f"Limpado {input_path} e salvo em {output_path}")
    except Exception as e:
        logging.error(f"Erro ao limpar {input_path}: {e}")

def convert_pdf_to_docx(pdf_file_path, output_folder):
    docx_file_path = os.path.join(output_folder, os.path.splitext(os.path.basename(pdf_file_path))[0] + '.docx')
    if os.path.exists(docx_file_path):
        logging.info(f"O arquivo {docx_file_path} já foi convertido. Pulando conversão.")
        return docx_file_path

    try:
        cv = Converter(pdf_file_path)
        cv.convert(docx_file_path, start=0, end=None)
        cv.close()
        logging.info(f"Convertido {pdf_file_path} para {docx_file_path}")
        return docx_file_path
    except Exception as e:
        logging.error(f"Erro ao converter {pdf_file_path}: {e}")
        return None

def process_pdf(pdf_file_path, output_folder):
    try:
        docx_file_path = os.path.join(output_folder, os.path.splitext(os.path.basename(pdf_file_path))[0] + '.docx')
        if os.path.exists(docx_file_path):
            logging.info(f"O arquivo {docx_file_path} já foi convertido. Pulando conversão.")
            return docx_file_path

        optimized_pdf_path = os.path.join(output_folder, 'optimized_' + os.path.basename(pdf_file_path))
        optimize_pdf(pdf_file_path, optimized_pdf_path)

        cleaned_pdf_path = os.path.join(output_folder, 'cleaned_' + os.path.basename(pdf_file_path))
        clean_pdf(optimized_pdf_path, cleaned_pdf_path)

        docx_path = convert_pdf_to_docx(cleaned_pdf_path, output_folder)

        os.remove(optimized_pdf_path)
        os.remove(cleaned_pdf_path)

        return docx_path

    except Exception as e:
        logging.error(f"Erro ao processar {pdf_file_path}: {e}")
        return None

def process_all_pdfs(input_folder, output_folder):
    num_threads = 8
    logging.info(f"Usando {num_threads} threads para processamento.")

    pdf_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_pdf, pdf_file, output_folder) for pdf_file in pdf_files]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(pdf_files), desc="Processando PDFs"):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Erro ao processar PDF: {e}")

def merge_pdfs(pdf_folder, output_folder, output_filename):
    output_path = os.path.join(output_folder, f'{output_filename}.pdf')
    if os.path.exists(output_path):
        logging.info(f"PDF já unido: {output_path}")
        return output_path

    pdf_writer = PdfWriter()
    pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    pdf_files.sort()

    logging.info(f"Tentando unir {len(pdf_files)} arquivos PDF em {output_path}")
    for pdf in pdf_files:
        try:
            pdf_reader = PdfReader(pdf)
            if not pdf_reader.pages:
                logging.error(f"Arquivo PDF {pdf} está vazio, pulando.")
                continue
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])
        except Exception as e:
            logging.error(f"Erro ao unir o arquivo PDF {pdf}: {e}")

    if pdf_files:
        try:
            with open(output_path, "wb") as output_pdf:
                pdf_writer.write(output_pdf)
            logging.info(f"PDFs unidos em: {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Erro ao salvar o PDF unido {output_path}: {e}")
            return None
    return None
