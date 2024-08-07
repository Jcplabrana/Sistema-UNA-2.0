import os
import re
import logging
from bs4 import BeautifulSoup

def extract_data_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    rows = soup.find_all('tr', id=True)
    data = []
    for row in rows:
        if 'objeto' in row['id']:
            item = {}
            try:
                item['Objeto'] = row.find_all('td')[1].text.strip() if row else ""
                modalidade_row = row.find_next_sibling('tr', id=lambda x: x and 'modalidade' in x)
                modalidade_text = modalidade_row.find_all('td')[1].text.strip() if modalidade_row else ""
                match = re.match(r"([A-Za-z]+)\/([0-9\/]+)", modalidade_text)
                if match:
                    item['Modalidade'] = match.group(1)
                    item['N Licitação'] = match.group(2)
                else:
                    item['Modalidade'] = modalidade_text
                    item['N Licitação'] = ""
                orgao_row = row.find_next_sibling('tr', id=lambda x: x and 'orgao' in x)
                item['Órgão Licitante'] = orgao_row.find_all('td')[1].text.strip() if orgao_row else ""
                data_abertura_row = row.find_next_sibling('tr', id=lambda x: x and 'dataAbertura' in x)
                if data_abertura_row:
                    item['Prazo Abertura'] = data_abertura_row.find_all('td')[1].text.strip()
                    item['Prazo (Hora)'] = data_abertura_row.find_all('td')[3].text.strip()
                cidade_row = row.find_next_sibling('tr', id=lambda x: x and 'cidade' in x)
                if cidade_row:
                    item['Cidade'] = cidade_row.find_all('td')[1].text.strip()
                    item['UF'] = cidade_row.find_all('td')[3].text.strip()
                link_edital_row = row.find_next_sibling('tr', id=lambda x: x and 'linkEdital' in x)
                a_tag = link_edital_row.find('a') if link_edital_row else None
                item['Acesso'] = a_tag['href'] if a_tag and 'href' in a_tag.attrs else ""
                observacao_row = row.find_next_sibling('tr', id=lambda x: x and 'observacao' in x)
                item['Observações'] = observacao_row.find_all('td')[1].text.strip() if observacao_row else ""
                valor_edital_match = re.search(r'R\$\s*([\d\.,]+)', item['Observações'])
                item['Valor Edital'] = valor_edital_match.group(1) if valor_edital_match else ""
                uasg_match = re.search(r'UASG:\s*(\d+)', item['Observações'])
                item['UASG'] = uasg_match.group(1) if uasg_match else ""

                item['Arquivo de Origem'] = os.path.basename(file_path)

                data.append(item)
            except (AttributeError, IndexError):
                continue
    return data
