import re
from typing import Dict, List

import PyPDF2
import pandas as pd
import streamlit as st
from stqdm import stqdm

RESTRUCT_AGREEMENT_COLS = [
    "restruct_agreement_city",
    "restruct_agreement_date"
    "restruct_agreement_customer_name",
    "restruct_agreement_contract_number",
    "restruct_agreement_contract_date",
    "restruct_agreement_amount",
    "restruct_agreement_due_date"
]


def extract_city(s):
    pattern = r'г\.\s([^., ]+)'
    result = re.findall(pattern, s, re.IGNORECASE)
    return result[0] if result else None


def extract_dates(s):
    pattern = r'\d{2}\.\d{2}\.\d{4}'
    return re.findall(pattern, s, re.IGNORECASE) or [None, None, None]


def extract_names(s):
    pattern = r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)'
    return re.findall(pattern, s) or [None, None]


def extract_contract_number(s):
    pattern = r'№\s+(\d+)'
    matches = re.findall(pattern, s)
    return matches[0] if matches else None


def extract_agreement_amount(s):
    pattern = r'(\d+)\s+рублей\s+(\d+)\s+копеек'
    amount = None
    amount_matches = re.search(pattern, s)
    if amount_matches:
        rubles = amount_matches.group(1)
        kopeks = amount_matches.group(2)
        amount = float(rubles + '.' + kopeks)

    return amount


def collect_restruct_agreement_data(pdf_dict: List[Dict[str, PyPDF2.PdfFileReader]]):
    """
    :param pdf_dict:
    :return:
    """
    result = []

    for file, _ in zip(pdf_dict, stqdm(range(len(pdf_dict)))):
        file_name, pdf_reader = file.get('file_name'), file.get('pdf_reader')
        try:

            first_page_data = pdf_reader.getPage(0).extract_text().replace('\n', " ")

            # extract_data from first page
            city = extract_city(first_page_data)

            dates = extract_dates(first_page_data)
            restruct_agreement_date, restruct_agreement_contract_date, restruct_agreement_due_date = dates

            name = extract_names(first_page_data)
            restruct_agreement_customer_name = name[1]

            restruct_agreement_contract_number = extract_contract_number(first_page_data)

            restruct_agreement_amount = extract_agreement_amount(first_page_data)

            result.append({
                "file": file_name,
                "restruct_agreement_city": city,
                "restruct_agreement_date": restruct_agreement_date,
                "restruct_agreement_customer_name": restruct_agreement_customer_name,
                "restruct_agreement_contract_number": restruct_agreement_contract_number,
                "restruct_agreement_contract_date": restruct_agreement_contract_date,
                "restruct_agreement_amount": restruct_agreement_amount,
                "restruct_agreement_due_date": restruct_agreement_due_date
            })

        except Exception as e:
            st.error(f'Ошибка разспознавания документа {file_name}')
            result.append({
                "file": file_name,
                "restruct_agreement_city": None,
                "restruct_agreement_date": None,
                "restruct_agreement_customer_name": None,
                "restruct_agreement_contract_number": None,
                "restruct_agreement_contract_date": None,
                "restruct_agreement_amount": None,
                "restruct_agreement_due_date": None
            })

    return pd.DataFrame(result)
